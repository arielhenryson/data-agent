from google.adk.agents import Agent
from .tools import (
    run_sql_query,
    run_api_query,
)

query_agent = Agent(
    name="query_agent",
    model="gemini-2.0-flash",
    description="An agent that can query various data sources",
    instruction=(
        "Your goal is the execute the plan of the parent agent and answer the user's query. "
        "If you can try to complete the task without asking questions from the user, do so."
    ),
    tools=[
        run_sql_query,
        run_api_query,
    ],
    
)