import os
import sys
import json
import subprocess
from typing import Optional

import psycopg2
import sqlite3 # Added for SQLite support
import requests

from .data_source_manager import DataSourceManager

def list_available_data_sources() -> str:
    """Lists all available data sources from the configuration file."""
    return DataSourceManager().list_sources_as_text()

def read_file_data_source(data_source_name: str) -> str:
    """
    Reads content from a file data source, which can be a local file or a URL.
    This is used to provide text-based context to the LLM.
    Args:
        data_source_name (str): The name of the file data source as defined in the YAML config.
    """
    try:
        manager = DataSourceManager()
        source_config = manager.get_source(data_source_name)
        
        if source_config.get('type') != 'file':
            return f"Error: Data source '{data_source_name}' is not a 'file' source."
            
        path = source_config.get('path')
        if not path:
            return f"Error: File data source '{data_source_name}' is missing the 'path' attribute in the configuration."

        # Check if the path is a URL
        if path.startswith('http://') or path.startswith('https://'):
            response = requests.get(path)
            response.raise_for_status() # Raise an exception for bad status codes
            return response.text
        else: # Treat as a local file path
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

    except (ValueError, requests.exceptions.RequestException, FileNotFoundError) as e:
        return f"Error reading file data source '{data_source_name}': {e}"

def get_db_schema_and_sample_data(data_source_name: str) -> str:
    """
    Get the database schema and sample data for a specific data source.
    Args:
        data_source_name (str): The name of the data source as defined in the YAML config.
    """
    db = None
    try:
        manager = DataSourceManager()
        source_config = manager.get_source(data_source_name)
        db = manager.get_db_connection(source_name=data_source_name)
        
        db_type = source_config.get('type')

        if db_type == 'postgres':
            schema_info = db.get_schema_as_text(ignore_tables=["vectors"])
            sample_data = db.get_table_samples_as_text(ignore_tables=["vectors"])
            return schema_info + "\n" + sample_data
        elif db_type == 'sqlite':
            # The SQLiteDB class provides the schema directly.
            # A sample data function could be added to the SQLiteDB class if needed.
            schema_info = db.get_schema_as_text()
            return schema_info
        else:
            return f"Error: Data source '{data_source_name}' is not a supported database type for schema retrieval."

    except (ValueError, ConnectionError, psycopg2.Error, sqlite3.Error) as e:
        return f"Error: {e}"
    finally:
        if db:
            # Gracefully close either a Postgres or SQLite connection
            if hasattr(db, 'disconnect'):
                db.disconnect()
            elif hasattr(db, 'close'):
                db.close()


def get_api_schema(data_source_name: str) -> str:
    """
    Get the OpenAPI schema for a specific API data source.
    Args:
        data_source_name (str): The name of the API data source as defined in the YAML config.
    """
    try:
        source_config = DataSourceManager().get_source(data_source_name)
        if source_config['type'] != 'openapi':
            return f"Error: Data source '{data_source_name}' is not an OpenAPI source."
        
        response = requests.get(source_config['spec_url'])
        response.raise_for_status()
        return response.text
    except (ValueError, requests.exceptions.RequestException) as e:
        return f"Error fetching API schema for '{data_source_name}': {e}"

def run_api_query(data_source_name: str, endpoint: str, method: str = "GET", data: Optional[dict] = None) -> str:
    """
    Run a query against a specific API data source.
    Args:
        data_source_name (str): The name of the API data source as defined in the YAML config.
        endpoint (str): The endpoint to query (e.g., 'users/1').
        method (str): The HTTP method (GET, POST, etc.).
        data (dict): The JSON data for POST/PUT requests.
    """
    try:
        source_config = DataSourceManager().get_source(data_source_name)
        if source_config['type'] != 'openapi':
            return f"Error: Data source '{data_source_name}' is not an OpenAPI source."
        
        base_url = source_config['base_url']
        full_url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        response = requests.request(method, full_url, json=data)
        response.raise_for_status()
        return response.text
    except (ValueError, requests.exceptions.RequestException) as e:
        return f"Error executing API query for '{data_source_name}': {e}"

def get_data_source_credentials(data_source_name: str) -> str:
    """
    Gets the credential mapping for a given data source.
    This returns a JSON string showing which environment variables correspond to
    database connection parameters like host, port, user, etc.
    Use this to know which environment variables to use when writing a Prefect flow.

    Args:
        data_source_name (str): The name of the data source as defined in the YAML config.
    """
    try:
        source_config = DataSourceManager().get_source(data_source_name)
        creds = source_config.get('credentials')
        if not creds:
            return f"Error: No credential mapping found for data source '{data_source_name}'."
        return json.dumps(creds, indent=2)
    except ValueError as e:
        return f"Error: {e}"

def save_prefect_flow(flow_name: str, flow_content: str) -> str:
    """
    Saves a generated Prefect flow to the 'flows' directory as a Python file.

    The LLM must follow these steps to generate the flow_content:
    1.  **If database access is needed, first call the `get_data_source_credentials` tool**
        with the appropriate `data_source_name`. This will provide the correct environment
        variable names for the database connection.
    2.  Generate the complete Python code for the flow. The code MUST:
        a. Include necessary imports like `from prefect import task, flow`, `os`, and `from dotenv import load_dotenv`.
        b. Call `load_dotenv(dotenv_path="../.env")` to load variables from the .env file.
        c. Use the specific environment variable names obtained in step 1 to access credentials
           (e.g., `os.getenv("BANK_DB_HOST")`, `os.getenv("BANK_DB_USER")`, etc.).
        d. Define tasks with the `@task` decorator and a flow with the `@flow` decorator.
        e. Include a main execution block (`if __name__ == "__main__":`) to run the flow.
    3.  Call this tool (`save_prefect_flow`) with the `flow_name` and the generated `flow_content`.

    Args:
        flow_name (str): The name for the flow file (e.g., 'my_etl_flow').
                         The '.py' extension will be added automatically.
        flow_content (str): The complete Python code string representing the Prefect flow.
    """
    FLOW_DIR = "flows"
    try:
        os.makedirs(FLOW_DIR, exist_ok=True)
        if "from prefect import" not in flow_content or "@flow" not in flow_content:
            return "Error: The provided flow_content does not appear to be a valid Prefect flow."
        file_path = os.path.join(FLOW_DIR, f"{flow_name}.py")
        with open(file_path, 'w') as f: f.write(flow_content)
        return f"✅ Prefect flow '{flow_name}.py' was successfully saved."
    except Exception as e:
        return f"❌ An error occurred while saving the Prefect flow: {e}"


def run_prefect_flow(flow_name: str) -> str:
    """Executes a previously saved Prefect flow Python file."""
    FLOW_DIR = "flows"
    file_path = os.path.join(FLOW_DIR, f"{flow_name}.py")
    if not os.path.exists(file_path):
        return f"❌ Error: Flow file '{flow_name}.py' not found."
    try:
        python_executable = sys.executable
        result = subprocess.run([python_executable, file_path], capture_output=True, text=True, check=True, timeout=60)
        output = f"--- STDOUT ---\n{result.stdout}"
        if result.stderr: output += f"\n--- STDERR ---\n{result.stderr}"
        return f"✅ Prefect flow '{flow_name}.py' executed successfully.\n{output}"
    except subprocess.CalledProcessError as e:
        return f"❌ Error executing Prefect flow '{flow_name}.py'.\nExit Code: {e.returncode}\n--- STDOUT ---\n{e.stdout}\n--- STDERR ---\n{e.stderr}"
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"
