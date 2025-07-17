from db import PostgresDB
from pydantic_ai import Agent
from dotenv import load_dotenv
from instrument import logfire
from pydantic_ai.messages import ModelMessage # Import for type hinting
import chainlit as cl

load_dotenv()

agent = Agent(
    'google-gla:gemini-2.5-flash',
    system_prompt='Your task is Answer the user query if you need to run a SQL query first get the database schema and sample data.',
)

@agent.tool
def get_db_schema_and_sample_data(run_context):
    """Get the database schema and sample data."""
    ignore_tables = ["vectors"]
    db = PostgresDB()
    db.connect()
    sample_data = db.get_table_samples_as_text(ignore_tables=ignore_tables)
    schema_info = db.get_schema_as_text(ignore_tables=ignore_tables)

    if schema_info and sample_data:
        full_context_for_llm = schema_info + sample_data

    return full_context_for_llm

@agent.tool_plain
def run_sql_query(query: str) -> str:
    """
    Run a SQL query against the database and return the results.
    Args:
        query: The SQL query string to execute.
    """
    try:
        db = PostgresDB()
        db.connect()
        query_result = db.query(query)
        return query_result
    except Exception as e:
        return f"Error executing query: {e}. Please check your SQL syntax and table/column names."

@cl.on_chat_start
async def start():
    cl.user_session.set("message_history", [])

@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")  # type: list[ModelMessage]

    # 2. Pass the current message history to the agent on each run
    result = await agent.run(message.content, message_history=message_history)

    # 3. Update the history with the messages from the completed run
    cl.user_session.set("message_history", result.all_messages())

    # Send the final answer
    await cl.Message(content=result.output).send()
    