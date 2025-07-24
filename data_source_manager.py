import yaml
import os
from db import PostgresDB

class DataSourceManager:
    """Loads and manages data sources from a YAML configuration file."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataSourceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path="data_sources.yaml"):
        if not hasattr(self, '_initialized'):
            self.config_path = config_path
            self.sources = self._load_sources()
            self._initialized = True

    def _load_sources(self):
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return {source['name']: source for source in config.get('data_sources', [])}
        except FileNotFoundError:
            print(f"Error: Configuration file not found at '{self.config_path}'")
            return {}
        except Exception as e:
            print(f"Error parsing YAML file: {e}")
            return {}

    def get_source(self, name: str):
        """Returns the configuration for a named data source."""
        source = self.sources.get(name)
        if not source:
            raise ValueError(f"Data source '{name}' not found in configuration.")
        return source

    def list_sources_as_text(self) -> str:
        """Returns a formatted string of available data sources for the LLM."""
        if not self.sources:
            return "No data sources are configured."
        
        output = "Here are the available data sources:\n\n"
        for name, details in self.sources.items():
            output += f"- Name: {name}\n"
            output += f"  Type: {details['type']}\n"
            output += f"  Description: {details['description']}\n\n"
        return output

    def get_db_connection(self, source_name: str):
        """Creates and returns a PostgresDB connection for a given source."""
        source_config = self.get_source(source_name)
        if source_config.get('type') != 'postgres':
            raise ValueError(f"Data source '{source_name}' is not a PostgreSQL database.")
        
        cred_keys = source_config.get('credentials')
        if not cred_keys:
            raise ValueError(f"Credential mapping not defined for data source '{source_name}' in the YAML file.")

        db_params = {
            "host": os.getenv(cred_keys.get('host_env')),
            "port": os.getenv(cred_keys.get('port_env')),
            "dbname": os.getenv(cred_keys.get('dbname_env')),
            "user": os.getenv(cred_keys.get('user_env')),
            "password": os.getenv(cred_keys.get('password_env'))
        }
        
        missing_params = [k for k, v in db_params.items() if v is None]
        if missing_params:
            raise ConnectionError(f"Missing environment variables for data source '{source_name}'. Please set: {missing_params}")

        return PostgresDB(**db_params)