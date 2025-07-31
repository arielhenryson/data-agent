from typing import Optional

import psycopg2
import requests
import sqlite3
from ...data_source_manager import DataSourceManager

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