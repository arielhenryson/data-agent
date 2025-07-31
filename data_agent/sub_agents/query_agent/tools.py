from typing import Optional

import psycopg2
import requests
import sqlite3
from ...data_source_manager import DataSourceManager
import json

def run_sql_query(data_source_name: str, query: str) -> str:
    """
    Run a SQL query against a specific data source.
    Args:
        data_source_name (str): The name of the data source as defined in the YAML config.
        query (str): The SQL query string to execute.
    """
    db = None
    try:
        manager = DataSourceManager()
        source_config = manager.get_source(data_source_name)
        db = manager.get_db_connection(source_name=data_source_name)
        
        db_type = source_config.get('type')

        if db_type == 'postgres':
            # Assumes the PostgresDB class has a 'query' method
            result = db.query(query)
        elif db_type == 'sqlite':
            # Assumes the SQLiteDB class has an 'execute_query' method
            result = db.execute_query(query)
        else:
            return f"Error: Cannot run SQL query on source type '{db_type}'."

        return str(result)
    except (ValueError, ConnectionError, psycopg2.Error, sqlite3.Error) as e:
        return f"Error: {e}"
    finally:
        if db:
            if hasattr(db, 'disconnect'):
                db.disconnect()
            elif hasattr(db, 'close'):
                db.close()

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



def read_json_data_source(data_source_name: str) -> str:
    """
    Reads data from a JSON data source, which can be a local file or a URL.
    Args:
        data_source_name (str): The name of the JSON data source as defined in the YAML config.
    """
    try:
        manager = DataSourceManager()
        source_config = manager.get_source(data_source_name)
        
        if source_config.get('type') != 'json':
            return f"Error: Data source '{data_source_name}' is not a JSON source."
            
        path = source_config.get('path')
        if not path:
            return f"Error: JSON data source '{data_source_name}' is missing the 'path' attribute in the configuration."

        # Check if the path is a URL
        if path.startswith('http://') or path.startswith('https://'):
            response = requests.get(path)
            response.raise_for_status() # Raise an exception for bad status codes
            json_data = response.json()
        else: # Treat as a local file path
            with open(path, 'r') as f:
                json_data = json.load(f)
        
        # Return the data as a formatted JSON string
        return json.dumps(json_data, indent=2)

    except (ValueError, requests.exceptions.RequestException, FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading JSON data source '{data_source_name}': {e}"