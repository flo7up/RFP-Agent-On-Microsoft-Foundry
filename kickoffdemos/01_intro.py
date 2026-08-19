"""Demo 1: turn one customer opportunity into a partner solution assessment.

Capability: Publishes a project-managed prompt agent and invokes that exact version through
FoundryAgent to produce a structured brief with delivery risks and human oversight.
Shows: A useful model-only baseline before adding organizational data or enterprise tools.
"""

import argparse
import asyncio
import os
from pathlib import Path

from agent_framework.foundry import FoundryAgent
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity.aio import AzureCliCredential
from agent_framework import tool
from dotenv import load_dotenv


DEFAULT_OPPORTUNITY = (
    Path(__file__).resolve().parents[1] / "data" / "default_opportunity.txt"
).read_text(encoding="utf-8").strip()

agent_name = "partner-solution-assessment-intro"
agent_instructions = (
    "You are a Microsoft partner solution architect. Assess the customer opportunity and return "
    "four short sections with these exact headings: AI Opportunities, Architecture Proposal, "
    "Delivery Risks, and Executive Summary. Recommend Microsoft Agent Framework and Microsoft "
    "Foundry when they fit. State assumptions, include human oversight, and stay under 220 words."
)


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
        ),
        description="Assesses customer opportunities for a Microsoft partner.",
    )
    return FoundryAgent(
        project_client=project_client,
        agent_name=agent_version.name,
        agent_version=agent_version.version,
        default_options={"store": False},
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("opportunity", nargs="?", default=DEFAULT_OPPORTUNITY)
    args = parser.parse_args()

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
        response = await agent.run(args.opportunity)
        print(response.text)


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
