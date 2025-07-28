from google.adk.agents import Agent
from .tools import (
    list_available_data_sources,
    get_db_schema_and_sample_data,
    get_data_source_credentials,
    run_sql_query,
    get_api_schema,
    run_api_query,
    save_prefect_flow,
    run_prefect_flow,
)

root_agent = Agent(
    name="data_agent",
    model="gemini-2.0-flash",
    description="An agent that can interact with various data sources like databases and APIs.",

    instruction=(
        "You are a helpful AI assistant. Your goal is to answer the user's query by interacting with configured data sources. "
        "First, you must determine which data source to use based on the user's prompt and the available sources. "
        "If you are unsure which data source to use, call the `list_available_data_sources` tool to see the options. "
        "Once you have identified the target, you MUST provide the `data_source_name` to all other tools (`run_sql_query`, `get_db_schema_and_sample_data`, etc.)."
    ),
    tools=[
        list_available_data_sources,
        get_db_schema_and_sample_data,
        get_data_source_credentials,
        run_sql_query,
        get_api_schema,
        run_api_query,
        save_prefect_flow,
        run_prefect_flow,
    ],
)