import requests
from db import PostgresDB
from pydantic_ai import Agent
import os
import json
import subprocess
import sys

# This assumes pydantic_ai and other dependencies are installed.
# A mock Agent class is provided for demonstration if pydantic_ai is not available.
try:
    from pydantic_ai import Agent
except ImportError:
    print("Warning: pydantic_ai not found. Using a mock Agent class for demonstration.")
    class Agent:
        def __init__(self, model, system_prompt):
            pass
        def tool(self, func):
            return func
        def tool_plain(self, func):
            return func

agent = Agent(
    'google-gla:gemini-2.5-flash',
    system_prompt='Your task is to answer the user query. If you need to run a SQL query, first get the database schema and sample data. When creating a Prefect flow, generate the full Python script.'
)

@agent.tool_plain
def save_prefect_flow(flow_name: str, flow_content: str) -> str:
    """
    Saves a generated Prefect flow to the 'flows' directory as a Python file.
    The LLM should first generate the complete Python code for the flow before calling this tool.

    The generated code MUST:
    1. Include necessary imports from 'prefect' (@task, @flow).
    2. If database access is required, it MUST load credentials from a .env file.
       - It should import `os` and `from dotenv import load_dotenv`.
       - It must call `load_dotenv(dotenv_path="../.env")` to load variables from the .env file
         located one directory above the 'flows' directory.
       - Access credentials using os.getenv("DB_HOST"), os.getenv("DB_USER"), etc.
       - The python-dotenv library is assumed to be installed in the environment.
    3. Define tasks with the @task decorator and a flow with the @flow decorator.
    4. Include a main execution block (`if __name__ == "__main__":`) to run the flow.

    Args:
        flow_name (str): The name for the flow file (e.g., 'my_etl_flow').
                         The '.py' extension will be added automatically.
        flow_content (str): The complete Python code string representing the Prefect flow.
    """
    FLOW_DIR = "flows"
    
    try:
        # Ensure the flow directory exists
        os.makedirs(FLOW_DIR, exist_ok=True)
        
        # Simple validation for Prefect code
        if "from prefect import" not in flow_content or "@flow" not in flow_content:
            return "Error: The provided flow_content does not appear to be a valid Prefect flow. It should contain 'from prefect import' and a '@flow' decorator."

        # Define the full file path
        file_path = os.path.join(FLOW_DIR, f"{flow_name}.py")
        
        # Write the content to the file
        with open(file_path, 'w') as f:
            f.write(flow_content)
            
        return f"✅ Prefect flow '{flow_name}.py' was successfully saved in the '{FLOW_DIR}' directory."
    except Exception as e:
        return f"❌ An error occurred while saving the Prefect flow: {e}"

@agent.tool_plain
def run_prefect_flow(flow_name: str) -> str:
    """
    Executes a previously saved Prefect flow Python file using the same Python interpreter
    and conda environment that this script is running in. This is equivalent to running
    `python <the-created-flow.py>` from the command line within the active environment.

    Args:
        flow_name (str): The name of the flow file to run (e.g., 'my_etl_flow'), 
                         without the '.py' extension.
    """
    FLOW_DIR = "flows"
    file_path = os.path.join(FLOW_DIR, f"{flow_name}.py")

    if not os.path.exists(file_path):
        return f"❌ Error: Flow file '{flow_name}.py' not found in the '{FLOW_DIR}' directory."

    try:
        # Get the path to the current python executable to ensure the flow runs
        # in the same conda environment as this script.
        python_executable = sys.executable
        
        # Execute the python script as a subprocess.
        result = subprocess.run(
            [python_executable, file_path],
            capture_output=True,
            text=True,
            check=True,  # Raise an exception for non-zero exit codes
            timeout=60   # Add a timeout for safety
        )
        
        output = f"--- STDOUT ---\n{result.stdout}"
        if result.stderr:
            output += f"\n--- STDERR ---\n{result.stderr}"

        return f"✅ Prefect flow '{flow_name}.py' executed successfully.\n{output}"

    except subprocess.CalledProcessError as e:
        return f"❌ Error executing Prefect flow '{flow_name}.py'.\nExit Code: {e.returncode}\n--- STDOUT ---\n{e.stdout}\n--- STDERR ---\n{e.stderr}"
    except subprocess.TimeoutExpired as e:
        return f"❌ Error: The flow '{flow_name}.py' timed out after {e.timeout} seconds."
    except Exception as e:
        return f"❌ An unexpected error occurred while running the flow: {e}"


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
    try:
        response = requests.get("http://0.0.0.0:8001/openapi.json")
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching API schema: {e}"


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
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error executing API query: {e}."


@agent.tool_plain
def run_sql_query(query: str) -> str:
    """
    Run a SQL query against the database and return the results.
    Args:
        query: The SQL query string to execute (run all on the public schema).
    """
    # This is a placeholder for your actual DB connection
    class PostgresDB:
        def connect(self): print("Connecting to DB...")
        def query(self, q): return f"Result of: {q}"

    print(f"Executing SQL Query: {query}")
    try:
        db = PostgresDB()
        db.connect()
        query_result = db.query(query)
        return str(query_result) # Ensure result is a string
    except Exception as e:
        return f"Error executing query: {e}. Please check your SQL syntax and table/column names."
