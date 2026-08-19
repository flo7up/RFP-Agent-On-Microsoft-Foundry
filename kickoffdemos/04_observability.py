"""Demo 4: export Agent Framework traces and record a custom evaluation score.

Capability: Sends agent telemetry to Application Insights, OTLP, or Foundry Toolkit and
records a lightweight enterprise-coverage evaluation on the same trace.
Shows: How observability and application-specific evaluation expose operational evidence.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import socket
from uuid import uuid4

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework.observability import (
    configure_otel_providers,
    enable_instrumentation,
    get_tracer,
)
from azure.identity import AzureCliCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace.span import format_trace_id


DEFAULT_PROMPT = (
    "Assess Contoso Health's prior-authorization agent. Include architecture, security, "
    "cost considerations, and an executive summary."
)


def create_agent(credential: AzureCliCredential) -> Agent:
    endpoint = (
        os.getenv("FOUNDRY_PROJECT_ENDPOINT")
        or os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        or os.getenv("project_endpoint")
    )
    model = (
        os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
        or os.getenv("FOUNDRY_MODEL")
        or os.getenv("deployment_name")
    )
    if not endpoint or not model:
        raise RuntimeError(
            "Set FOUNDRY_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME before running the demo."
        )
    return Agent(
        name="partner-solution-assessment",
        instructions=(
            "Return exactly four concise sections: Architecture Recommendation, Security Considerations, "
            "Cost Considerations, and Executive Summary. Include human approval and observability."
        ),
        client=FoundryChatClient(
            project_endpoint=endpoint,
            model=model,
            credential=credential,
        ),
        default_options={"store": False},
    )


def configure_tracing(include_content: bool) -> str:
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if connection_string:
        configure_azure_monitor(
            connection_string=connection_string,
            enable_live_metrics=False,
            resource=Resource.create(
                {
                    "service.name": "partner-solution-assessment",
                    "service.namespace": "opportunity-assessment-agent",
                }
            ),
        )
        enable_instrumentation(enable_sensitive_data=include_content, force=True)
        return "Microsoft Foundry / Application Insights"

    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        configure_otel_providers(enable_sensitive_data=include_content)
        return "the configured OpenTelemetry endpoint"

    try:
        with socket.create_connection(("127.0.0.1", 4317), timeout=0.2):
            viewer_is_open = True
    except OSError:
        viewer_is_open = False

    configure_otel_providers(
        vs_code_extension_port=4317 if viewer_is_open else None,
        enable_sensitive_data=include_content,
        enable_console_exporters=False,
    )
    if viewer_is_open:
        return "Foundry Toolkit trace viewer on localhost:4317"
    return "local spans only; open the Foundry Toolkit trace viewer before the live run"


def enterprise_coverage(text: str) -> tuple[float, list[str]]:
    criteria = {
        "architecture": "architecture",
        "security": "security",
        "cost": "cost",
        "executive summary": "executive summary",
        "human approval": "human approval",
        "observability": "observability",
    }
    normalized = text.lower()
    missing = [label for label, phrase in criteria.items() if phrase not in normalized]
    return (len(criteria) - len(missing)) / len(criteria), missing


def flush_telemetry() -> None:
    provider = trace.get_tracer_provider()
    force_flush = getattr(provider, "force_flush", None)
    if callable(force_flush):
        force_flush(timeout_millis=5_000)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--include-content",
        action="store_true",
        help="Capture prompts and completions. Use only with non-sensitive demo data.",
    )
    args = parser.parse_args()
    destination = configure_tracing(args.include_content)
    scenario_id = f"partner-demo-{uuid4().hex[:8]}"
    credential = AzureCliCredential()

    try:
        print("\nDEMO 4 - EVALUATION + TRACING")
        print(f"Telemetry destination: {destination}")
        tracer = get_tracer("partner-kickoff-demo")
        with tracer.start_as_current_span("partner.solution_assessment") as span:
            span.set_attribute("demo.scenario_id", scenario_id)
            span.set_attribute("demo.customer_industry", "healthcare")
            span.set_attribute("demo.content_capture_enabled", args.include_content)
            span_context = span.get_span_context()
            trace_id = (
                format_trace_id(span_context.trace_id)
                if span_context.is_valid
                else "unavailable (no active telemetry exporter)"
            )

            response = await create_agent(credential).run(args.prompt)
            score, missing = enterprise_coverage(response.text)
            span.set_attribute("evaluation.enterprise_coverage", score)
            span.set_attribute("evaluation.missing_criteria", ",".join(missing) or "none")
            span.add_event("evaluation.completed", {"evaluation.score": score})

        print(f"Trace ID: {trace_id}")
        print(f"Enterprise coverage score: {score:.0%}")
        print(f"Missing criteria: {', '.join(missing) if missing else 'none'}")
        print("Inspect the trace for agent/model spans, latency, token usage, errors, and this evaluation score.")
    finally:
        try:
            flush_telemetry()
        finally:
            credential.close()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
