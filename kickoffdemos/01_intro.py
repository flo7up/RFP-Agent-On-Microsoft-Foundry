"""Demo 1: turn one customer opportunity into a partner solution assessment."""

from __future__ import annotations

import argparse
import asyncio
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv


DEFAULT_OPPORTUNITY = (
    "Contoso Health wants to reduce prior-authorization preparation from two hours "
    "to fifteen minutes. Staff must use approved clinical records, keep patient data "
    "inside the tenant, and require a clinician to approve every submission."
)


def create_client(credential: AzureCliCredential) -> FoundryChatClient:
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
    return FoundryChatClient(
        project_endpoint=endpoint,
        model=model,
        credential=credential,
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("opportunity", nargs="?", default=DEFAULT_OPPORTUNITY)
    args = parser.parse_args()

    credential = AzureCliCredential()
    try:
        agent = Agent(
            name="partner-solution-assessment",
            description="Assesses customer opportunities for a Microsoft partner.",
            instructions=(
                "You are a Microsoft partner solution architect. Assess the customer opportunity and return "
                "four short sections with these exact headings: AI Opportunities, Architecture Proposal, "
                "Delivery Risks, and Executive Summary. Recommend Microsoft Agent Framework and Microsoft "
                "Foundry when they fit. State assumptions, include human oversight, and stay under 220 words."
            ),
            client=create_client(credential),
            default_options={"store": False},
        )

        print("\nDEMO 1 - SINGLE AGENT")
        print("One Agent Framework agent turns an opportunity into an architecture-ready brief.\n")
        response = await agent.run(args.opportunity)
        print(response.text)
    finally:
        credential.close()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
