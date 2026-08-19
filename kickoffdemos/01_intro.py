"""Demo 1: turn one customer opportunity into a partner solution assessment.

Capability: Publishes a project-managed prompt agent that reads the customer opportunity
through an Agent Framework tool before producing a structured partner assessment.
Shows: A useful model-only baseline before adding organizational data or enterprise tools.
"""

import argparse
import asyncio
import os
from pathlib import Path

from agent_framework import tool
from agent_framework.foundry import FoundryAgent
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import FunctionTool as FoundryFunctionTool
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv


OPPORTUNITY_FILE = Path(__file__).resolve().parents[1] / "data" / "default_opportunity.txt"
EMPTY_FUNCTION_PARAMETERS = {"type": "object", "properties": {}, "additionalProperties": False}

agent_name = "demo-01-partner-solution-assessment"
agent_instructions = (
    "You are a Microsoft partner solution architect. Before answering, call opportunity_tool "
    "exactly once and use its result as the only source of customer facts. Return "
    "four short sections with these exact headings: AI Opportunities, Architecture Proposal, "
    "Delivery Risks, and Executive Summary. Recommend Microsoft Agent Framework and Microsoft "
    "Foundry when they fit. State assumptions, include human oversight, and stay under 220 words."
)


@tool(
    name="opportunity_tool",
    description="Return the complete customer opportunity.",
    approval_mode="never_require",
    schema=EMPTY_FUNCTION_PARAMETERS,
)
def get_opportunity() -> str:
    return OPPORTUNITY_FILE.read_text(encoding="utf-8").strip()


def required_setting(*names: str) -> str:
    for name in names:
        if value := os.getenv(name):
            return value
    raise RuntimeError(f"Set one of these environment variables: {', '.join(names)}")


async def create_agent(project_client: AIProjectClient, model_deployment_name: str) -> FoundryAgent:
    agent_version = await project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_deployment_name,
            instructions=agent_instructions,
            tools=[
                FoundryFunctionTool(
                    name=get_opportunity.name,
                    description=get_opportunity.description or "",
                    parameters=get_opportunity.parameters(),
                    strict=True,
                )
            ],
        ),
        description="Assesses customer opportunities for a Microsoft partner.",
    )
    return FoundryAgent(
        project_client=project_client,
        agent_name=agent_version.name,
        agent_version=agent_version.version,
        tools=[get_opportunity],
        default_options={"store": False},
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    project_endpoint = required_setting(
        "FOUNDRY_PROJECT_ENDPOINT",
        "AZURE_AI_PROJECT_ENDPOINT",
        "project_endpoint",
    )
    model_deployment_name = required_setting(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME",
        "FOUNDRY_MODEL",
        "deployment_name",
    )

    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
    ):
        agent = await create_agent(project_client, model_deployment_name)

        print("\nDEMO 1 - SINGLE AGENT")
        print(
            f"Foundry agent {agent_name} turns an opportunity into an architecture-ready brief.\n"
        )
        response = await agent.run("Assess the customer opportunity available through opportunity_tool.")
        print(response.text)


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
