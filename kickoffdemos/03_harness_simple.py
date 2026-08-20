"""Demo 03 minimal Agent Harness example with one synthetic tool.

Run:
    python kickoffdemos/03_harness_simple.py
"""

import asyncio
import os

from agent_framework import create_harness_agent, tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv


@tool(approval_mode="never_require")
def get_weather(city: str) -> str:
    """Return synthetic weather for a city."""
    return f"{city}: sunny, 22 C (synthetic demo data)."


def create_agent(credential: AzureCliCredential):
    return create_harness_agent(
        client=FoundryChatClient(
            project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT") or os.environ["project_endpoint"],
            model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME") or os.environ["deployment_name"],
            credential=credential,
        ),
        agent_instructions="Always call get_weather before answering.",
        tools=[get_weather],
        disable_todo=True,
        disable_mode=True,
        disable_file_memory=True,
        disable_web_search=True,
        default_options={"store": False},
    )


async def main() -> None:
    credential = AzureCliCredential()
    try:
        agent = create_agent(credential)
        response = await agent.run("What is the weather in Seattle?", session=agent.create_session())
        print(response.text)
    finally:
        credential.close()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
