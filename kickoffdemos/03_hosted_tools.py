"""Demo 3: ground an agent with enterprise tools and optionally host it in Foundry.

Capability: Uses bounded CRM, architecture-guidance, and cost-profile tools, then runs the
same agent locally or behind the Foundry Responses hosting boundary.
Shows: How approved enterprise facts and governed tool calls improve a recommendation.
"""

from __future__ import annotations

import argparse
import asyncio
import os
from typing import Any

from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential, DefaultAzureCredential
from dotenv import load_dotenv


DEFAULT_PROMPT = (
    "Assess opportunity OPP-1042. Ground the recommendation in our customer record, "
    "approved architecture guidance, and an indicative Azure cost profile."
)
DEFAULT_OPPORTUNITY_ID = "OPP-1042"
DEFAULT_MONTHLY_REQUESTS = 12_000


@tool(
    name="get_opportunity_record",
    description="Read an approved customer opportunity record from the partner CRM.",
    approval_mode="never_require",
)
def get_opportunity_record(opportunity_id: str) -> str:
    print(f"  [tool] CRM lookup: {opportunity_id}")
    if opportunity_id.upper() != DEFAULT_OPPORTUNITY_ID:
        return "No approved opportunity record was found."
    return (
        "Customer: Contoso Health; target: prior-authorization preparation under 15 minutes; "
        "data: approved clinical records with PHI; controls: tenant isolation and clinician approval; "
        f"volume: {DEFAULT_MONTHLY_REQUESTS:,} requests per month."
    )


@tool(
    name="search_architecture_guidance",
    description="Search the partner's approved Microsoft architecture guidance.",
    approval_mode="never_require",
)
def search_architecture_guidance(topic: str) -> str:
    print(f"  [tool] Knowledge search: {topic}")
    return (
        "Approved pattern: Microsoft Agent Framework on Foundry Hosted Agents; managed identity; "
        "private networking; Azure AI Search for grounded retrieval; human approval before submission; "
        "Application Insights tracing with content capture disabled for production PHI."
    )


@tool(
    name="estimate_azure_service_profile",
    description="Return an illustrative Azure service profile using an approved opportunity's CRM volume.",
    approval_mode="never_require",
)
def estimate_azure_service_profile(opportunity_id: str) -> str:
    if opportunity_id.upper() != DEFAULT_OPPORTUNITY_ID:
        return "No approved opportunity volume was found for cost profiling."
    print(
        f"  [tool] Cost profile: {DEFAULT_OPPORTUNITY_ID} -> "
        f"{DEFAULT_MONTHLY_REQUESTS:,} requests/month"
    )
    return (
        f"Illustrative profile for {DEFAULT_MONTHLY_REQUESTS:,} requests/month. Services: Foundry model "
        "deployment, Foundry Hosted Agent, Azure AI Search, "
        "Application Insights, Key Vault, and private endpoints. Main cost drivers: model tokens, "
        "search capacity, retained telemetry, and hosted-agent compute. Validate prices with the Azure "
        "Pricing Calculator before presenting a customer quote."
    )


def create_agent(credential: Any) -> Agent:
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
    client = FoundryChatClient(project_endpoint=endpoint, model=model, credential=credential)
    return Agent(
        name="partner-solution-assessment",
        description="Creates grounded partner solution assessments from enterprise systems.",
        instructions=(
            "You are a Microsoft partner solution architect. First call get_opportunity_record with the "
            "opportunity ID. Call all other relevant tools before answering. Pass that same opportunity ID "
            "to estimate_azure_service_profile so it uses the approved CRM volume; never invent or alter "
            "numeric tool inputs. Use only tool results for customer facts. Separate approved facts from "
            "assumptions, label cost information as illustrative, require human approval for high-impact "
            "actions, and return a concise executive recommendation."
        ),
        client=client,
        tools=[get_opportunity_record, search_architecture_guidance, estimate_azure_service_profile],
        default_options={"store": False},
    )


async def run_local(prompt: str) -> None:
    print("\nDEMO 3 - ENTERPRISE TOOLS + HOSTED AGENT")
    print("The same agent boundary runs locally or behind Foundry's Responses protocol.\n")
    credential = AzureCliCredential()
    try:
        response = await create_agent(credential).run(prompt)
        print("\nGROUNDED RECOMMENDATION\n")
        print(response.text)
    finally:
        credential.close()


def serve() -> None:
    try:
        from agent_framework_foundry_hosting import ResponsesHostServer
    except ImportError as error:
        raise RuntimeError(
            "Install agent-framework-foundry-hosting to run this file as a Hosted Agent."
        ) from error

    print("Starting the Foundry Responses host on the platform-managed endpoint.")
    credential = DefaultAzureCredential()
    try:
        ResponsesHostServer(create_agent(credential)).run()
    finally:
        credential.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="Run as a Foundry Hosted Agent entry point.")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    args = parser.parse_args()
    if args.serve:
        serve()
    else:
        asyncio.run(run_local(args.prompt))


if __name__ == "__main__":
    load_dotenv()
    main()
