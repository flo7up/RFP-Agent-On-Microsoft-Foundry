"""Loopback web host for the Demo 03 observable Harness playground."""

from __future__ import annotations

import asyncio
import json
import threading
import uuid
import webbrowser
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from azure.identity import AzureCliCredential


ASSET_DIR = Path(__file__).with_name("harness_playground_assets")
REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = (REPO_ROOT / "outputs").resolve()
MAX_REQUEST_BYTES = 64_000
Runner = Callable[..., Awaitable[tuple[str, list[Any]]]]


@dataclass
class ObservableRun:
    run_id: str
    opportunity: str
    events: list[dict[str, Any]] = field(default_factory=list)
    result_location: str | None = None
    is_complete: bool = False
    condition: threading.Condition = field(default_factory=threading.Condition)

    def publish(self, event: Any) -> None:
        payload = event.to_dict() if hasattr(event, "to_dict") else dict(event)
        with self.condition:
            payload["sequence"] = len(self.events) + 1
            payload["occurred_at"] = datetime.now(timezone.utc).isoformat()
            self.events.append(payload)
            self.condition.notify_all()

    def finish(self) -> None:
        with self.condition:
            self.is_complete = True
            self.condition.notify_all()


class RunRegistry:
    def __init__(self, runner: Runner, default_opportunity: str) -> None:
        self.runner = runner
        self.default_opportunity = default_opportunity
        self._runs: dict[str, ObservableRun] = {}
        self._lock = threading.Lock()

    def create(self, opportunity: str) -> ObservableRun:
        run = ObservableRun(run_id=uuid.uuid4().hex, opportunity=opportunity)
        with self._lock:
            self._runs[run.run_id] = run
        threading.Thread(target=self._execute, args=(run,), daemon=True).start()
        return run

    def get(self, run_id: str) -> ObservableRun | None:
        with self._lock:
            return self._runs.get(run_id)

    def _execute(self, run: ObservableRun) -> None:
        credential = AzureCliCredential()
        try:
            location, _ = asyncio.run(
                self.runner(
                    run.opportunity,
                    credential,
                    event=run.publish,
                )
            )
            run.result_location = location
        except Exception as exc:
            run.publish(
                {
                    "kind": "run.failed",
                    "location": "briefing_area",
                    "title": "Run failed",
                    "message": str(exc),
                    "status": "error",
                    "data": {},
                }
            )
        finally:
            credential.close()
            run.finish()


class PlaygroundServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], registry: RunRegistry) -> None:
        self.registry = registry
        super().__init__(address, PlaygroundHandler)


class PlaygroundHandler(BaseHTTPRequestHandler):
    server: PlaygroundServer

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/":
            self._send_asset("index.html", "text/html; charset=utf-8")
            return
        if route == "/assets/playground.css":
            self._send_asset("playground.css", "text/css; charset=utf-8")
            return
        if route == "/assets/playground.js":
            self._send_asset("playground.js", "text/javascript; charset=utf-8")
            return
        if route == "/api/config":
            self._send_json({"default_opportunity": self.server.registry.default_opportunity})
            return
        if route == "/api/health":
            self._send_json({"status": "ok"})
            return

        parts = route.strip("/").split("/")
        if len(parts) == 4 and parts[:2] == ["api", "runs"] and parts[3] == "events":
            self._stream_events(parts[2])
            return
        if len(parts) == 4 and parts[:2] == ["api", "runs"] and parts[3] == "document":
            self._send_document(parts[2])
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/runs":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid Content-Length")
            return
        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            self.send_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        try:
            body = json.loads(self.rfile.read(content_length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(HTTPStatus.BAD_REQUEST, "Expected a JSON body")
            return
        opportunity = body.get("opportunity") if isinstance(body, dict) else None
        if not isinstance(opportunity, str) or not opportunity.strip():
            self.send_error(HTTPStatus.BAD_REQUEST, "Opportunity is required")
            return
        run = self.server.registry.create(opportunity.strip())
        self._send_json(
            {
                "run_id": run.run_id,
                "events_url": f"/api/runs/{run.run_id}/events",
                "document_url": f"/api/runs/{run.run_id}/document",
            },
            status=HTTPStatus.ACCEPTED,
        )

    def _stream_events(self, run_id: str) -> None:
        run = self.server.registry.get(run_id)
        if run is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "close")
        self._send_security_headers()
        self.end_headers()

        last_event_id = self.headers.get("Last-Event-ID", "0")
        cursor = int(last_event_id) if last_event_id.isdigit() else 0
        try:
            while True:
                with run.condition:
                    if cursor >= len(run.events) and not run.is_complete:
                        run.condition.wait(timeout=15)
                    pending = run.events[cursor:]
                    is_complete = run.is_complete and cursor + len(pending) >= len(run.events)
                for event in pending:
                    body = json.dumps(event, ensure_ascii=True, separators=(",", ":"))
                    frame = f"id: {event['sequence']}\nevent: harness\ndata: {body}\n\n"
                    self.wfile.write(frame.encode("utf-8"))
                    self.wfile.flush()
                    cursor += 1
                if is_complete:
                    self.wfile.write(b"event: stream-end\ndata: {}\n\n")
                    self.wfile.flush()
                    self.close_connection = True
                    return
                if not pending:
                    self.wfile.write(b": keep-alive\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return

    def _send_document(self, run_id: str) -> None:
        run = self.server.registry.get(run_id)
        if run is None or not run.result_location:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        parsed = urlparse(run.result_location)
        if parsed.scheme in {"http", "https"}:
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", run.result_location)
            self._send_security_headers()
            self.end_headers()
            return

        output_path = (REPO_ROOT / run.result_location).resolve()
        if not output_path.is_relative_to(OUTPUT_ROOT) or not output_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = output_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/markdown; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{output_path.name}"')
        self.send_header("Content-Length", str(len(content)))
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(content)

    def _send_asset(self, name: str, content_type: str) -> None:
        path = ASSET_DIR / name
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload: dict[str, Any], *, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(content)

    def _send_security_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
            "connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'",
        )

    def log_message(self, format: str, *args: Any) -> None:
        return


def launch_playground(
    runner: Runner,
    *,
    default_opportunity: str,
    port: int = 8090,
    auto_open: bool = True,
) -> None:
    registry = RunRegistry(runner, default_opportunity)
    server = PlaygroundServer(("127.0.0.1", port), registry)
    url = f"http://127.0.0.1:{port}"
    print(f"Harness playground: {url}", flush=True)
    if auto_open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()