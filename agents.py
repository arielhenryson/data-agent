
import requests
from db import PostgresDB
from pydantic_ai import Agent
from instrument import logfire

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
    full_context_for_llm = ""

    if schema_info and sample_data:
        full_context_for_llm = schema_info + sample_data

    return full_context_for_llm

@agent.tool
def get_api_schema(run_context):
    """Get the Open API schema."""
    response = requests.get("http://0.0.0.0:8001/openapi.json")
    return response.text

@agent.tool_plain
def run_api_query(endpoint: str, method: str = "GET", data: dict = None) -> str:
    """
    Run a query against the API and return the results.
    Args:
        endpoint: The endpoint to query.
        method: The HTTP method to use (GET, POST, PUT, DELETE, etc.).
        data: The data to send with the request (for POST, PUT).
    """
    try:
        response = requests.request(method, f"http://0.0.0.0:8001/{endpoint}", json=data)
        return response.text
    except Exception as e:
        return f"Error executing query: {e}."


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