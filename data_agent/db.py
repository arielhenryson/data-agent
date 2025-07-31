import psycopg2
from psycopg2.extensions import AsIs
import sqlite3

class SQLiteDB:
    """A wrapper for a SQLite database connection."""
    def __init__(self, db_file: str):
        """
        Initializes the connection to the SQLite database.
        
        Args:
            db_file (str): The path to the SQLite database file.
        """
        try:
            self.db_file = db_file
            self.conn = sqlite3.connect(db_file)
            self.cursor = self.conn.cursor()
            print(f"Successfully connected to SQLite database: {db_file}")
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to SQLite database at {db_file}: {e}")

    def get_schema_as_text(self) -> str:
        """
        Retrieves the schema of all tables in the database and formats it as a string.
        
        Returns:
            str: A formatted string describing the table schemas.
        """
        try:
            self.cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
            tables = self.cursor.fetchall()
            if not tables:
                return "No tables found in the database."
            
            schema_str = "Database Schema:\n\n"
            for table_name, create_sql in tables:
                schema_str += f"-- Schema for table: {table_name}\n"
                schema_str += f"{create_sql};\n\n"
            return schema_str
        except sqlite3.Error as e:
            return f"Error retrieving schema: {e}"

    def execute_query(self, query: str):
        """
        Executes a given SQL query and fetches all results.
        
        Args:
            query (str): The SQL query to execute.
            
        Returns:
            list: A list of tuples representing the query results.
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise ValueError(f"Error executing query: {e}")

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print(f"SQLite connection to {self.db_file} closed.")

class PostgresDB:
    """A reusable class to interact with a specific PostgreSQL database."""
    def __init__(self, host, port, dbname, user, password):
        self.db_params = {
            "host": host, "port": port, "dbname": dbname, "user": user, "password": password
        }
        self.conn = None

    def connect(self):
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(**self.db_params)
            except psycopg2.Error as e:
                print(f"Error connecting to PostgreSQL database: {e}")
                raise

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def query(self, query, params=None):
        if self.conn is None: self.connect()
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                if query.strip().upper().startswith("SELECT"): return cur.fetchall()
                else: self.conn.commit(); return None
        except psycopg2.Error as e: self.conn.rollback(); raise e
    
    def get_schema_as_text(self, ignore_tables=None):
        if self.conn is None: self.connect()
        if ignore_tables is None: ignore_tables = []
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT table_name, column_name, data_type FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name NOT IN %s ORDER BY table_name, ordinal_position;
            """, (tuple(ignore_tables),))
            rows = cur.fetchall()
            schema = {}
            for table_name, column_name, data_type in rows:
                if table_name not in schema: schema[table_name] = []
                schema[table_name].append(f"{column_name} ({data_type})")
            schema_text = ""
            for table_name, columns in schema.items():
                schema_text += f"Table: {table_name}\nColumns:\n"
                for column in columns: schema_text += f"  - {column}\n"
                schema_text += "\n"
            return schema_text

    def get_table_samples_as_text(self, limit=10, ignore_tables=None):
        if self.conn is None: self.connect()
        if ignore_tables is None: ignore_tables = []
        with self.conn.cursor() as cur:
            cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' ORDER BY tablename;")
            all_tables = [row[0] for row in cur.fetchall()]
        ignore_set = set(ignore_tables)
        tables_to_query = [t for t in all_tables if t not in ignore_set]
        output_text = ""
        for table_name in tables_to_query:
            output_text += f"--- Sample data from table: {table_name} ---\n"
            try:
                with self.conn.cursor() as sample_cur:
                    query = "SELECT * FROM %s LIMIT %s"
                    sample_cur.execute(query, (AsIs(table_name), limit))
                    column_names = [desc[0] for desc in sample_cur.description]
                    output_text += ", ".join(column_names) + "\n"
                    rows = sample_cur.fetchall()
                    for row in rows:
                        output_text += ", ".join([str(cell) if cell is not None else 'NULL' for cell in row]) + "\n"
                    output_text += "\n"
            except psycopg2.Error as e:
                output_text += f"[Could not retrieve samples for table {table_name}: {e}]\n\n"
                self.conn.rollback()
        return output_text