"""Demo 03: host the Demo 02 opportunity-to-proposal workflow in Microsoft Foundry.

The Responses host exposes one bounded tool that executes Demo 02's two-stage hybrid
agentic retrieval, proposal generation, citation remapping, and Sources section assembly.
The hosted response returns the Markdown directly because container-local files are ephemeral.
"""

from __future__ import annotations

import importlib.util
import logging
import os
from pathlib import Path
from typing import Any

from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def load_patterns_workflow() -> Any:
    module_path = Path(__file__).with_name("02_patterns.py")
    spec = importlib.util.spec_from_file_location("hosted_patterns_workflow", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load the Demo 02 workflow from {module_path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


patterns_workflow = load_patterns_workflow()
logger = logging.getLogger(__name__)


def required_setting(*names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    raise RuntimeError(f"Set one of these environment variables: {', '.join(names)}")


async def create_grounded_proposal(opportunity: str, credential: Any) -> str:
    try:
        return await patterns_workflow.create_proposal(opportunity, credential)
    except Exception:
        logger.exception("The hosted opportunity proposal workflow failed.")
        raise


def create_proposal_tool(credential: Any) -> Any:
    @tool(
        name="create_grounded_opportunity_proposal",
        description=(
            "Create a complete cited Markdown proposal for a customer opportunity using the "
            "two-stage Foundry IQ opportunity and linked-proposal retrieval workflow."
        ),
        approval_mode="never_require",
    )
    async def create_grounded_opportunity_proposal(opportunity: str) -> str:
        return await create_grounded_proposal(opportunity, credential)

    return create_grounded_opportunity_proposal


def create_hosted_agent(credential: Any) -> Agent:
    endpoint = required_setting(
        "FOUNDRY_PROJECT_ENDPOINT",
        "AZURE_AI_PROJECT_ENDPOINT",
        "project_endpoint",
    )
    model = required_setting(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME",
        "FOUNDRY_MODEL",
        "deployment_name",
    )
    return Agent(
        name="opportunity-proposal-agent",
        description=(
            "Creates cited SI proposals by matching historical opportunities and retrieving "
            "their linked proposal patterns through Foundry IQ."
        ),
        instructions=(
            "You host the approved opportunity-to-proposal workflow. Treat the user's message as the "
            "new opportunity. Call create_grounded_opportunity_proposal exactly once with the complete "
            "opportunity text. Return the tool's Markdown verbatim without summarizing, rewriting, or "
            "adding commentary. Never invent customer facts or historical evidence."
        ),
        client=FoundryChatClient(
            project_endpoint=endpoint,
            model=model,
            credential=credential,
        ),
        tools=[create_proposal_tool(credential)],
        default_options={"store": False},
    )


def main() -> None:
    try:
        from agent_framework_foundry_hosting import ResponsesHostServer
    except ImportError as error:
        raise RuntimeError(
            "Install agent-framework-foundry-hosting before starting the hosted agent."
        ) from error

    credential = DefaultAzureCredential()
    try:
        ResponsesHostServer(create_hosted_agent(credential)).run()
    finally:
        credential.close()


if __name__ == "__main__":
    load_dotenv()
    main()