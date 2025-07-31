from google.adk.agents import Agent
from .tools import (
    list_available_data_sources,
    get_db_schema_and_sample_data,
    get_data_source_credentials,
    get_api_schema,
    read_json_data_source,
)
from .sub_agents.query_agent.agent import query_agent

root_agent = Agent(
    name="data_agent",
    model="gemini-2.0-flash",
    description="An agent that can interact with various data sources And plan how to query them.",
    instruction=(
        "Your goal is to answer the user's query by interacting with data sources. "
        "First, you must determine which data source to use based on the user's prompt"
        "Then use the appropriate tool to get the schema for the required data source"
        "Then create a plan on how to query the data source"
        "Delegate the task to the appropriate sub-agent. "
        "Never delegate the task before you have a plan on how to query the data source"
        "If you can try to complete the task without asking questions from the user, do so."
    ),
    tools=[
        list_available_data_sources,
        get_db_schema_and_sample_data,
        get_data_source_credentials,
        get_api_schema,
        read_json_data_source
    ],
    sub_agents=[
        query_agent,
    ],
)