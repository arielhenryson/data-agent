import os
import psycopg2
from psycopg2.extensions import AsIs
from dotenv import load_dotenv

load_dotenv()

class PostgresDB:
    def __init__(self):
        self.conn = None

    def connect(self):
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT"),
                    dbname=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD")
                )
                print("Connected to PostgreSQL database!")
            except psycopg2.Error as e:
                print(f"Error connecting to PostgreSQL database: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            print("Disconnected from PostgreSQL database.")

    def query(self, query, params=None):
        """
        Execute a query and return the results.
        """
        if self.conn is None:
            print("Not connected to a database.")
            return None

        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                if query.strip().upper().startswith("SELECT"):
                    return cur.fetchall()
                else:
                    self.conn.commit()
                    return None
        except psycopg2.Error as e:
            print(f"Error executing query: {e}")
            self.conn.rollback()
            return None

    def get_schema_as_text(self, ignore_tables=None):
        """
        Get the database schema as a text, with an option to ignore certain tables.
        
        Args:
            ignore_tables (list, optional): A list of table names to exclude.
        """
        if self.conn is None:
            print("Not connected to a database.")
            return None
        
        if ignore_tables is None:
            ignore_tables = []

        try:
            with self.conn.cursor() as cur:
                # SQL query to get schema info, excluding tables in the ignore list
                # psycopg2 can safely handle an empty tuple for the `IN` operator.
                cur.execute("""
                    SELECT table_name, column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name NOT IN %s
                    ORDER BY table_name, ordinal_position;
                """, (tuple(ignore_tables),))
                
                rows = cur.fetchall()
                schema = {}
                for table_name, column_name, data_type in rows:
                    if table_name not in schema:
                        schema[table_name] = []
                    schema[table_name].append(f"{column_name} ({data_type})")

                schema_text = ""
                for table_name, columns in schema.items():
                    schema_text += f"Table: {table_name}\n"
                    schema_text += "Columns:\n"
                    for column in columns:
                        schema_text += f"  - {column}\n"
                    schema_text += "\n"
                return schema_text
        except psycopg2.Error as e:
            print(f"Error getting schema: {e}")
            return None

    def get_table_samples_as_text(self, limit=10, ignore_tables=None):
        """
        For each table, fetches a sample of rows and returns them as formatted text.
        
        Args:
            limit (int): The number of rows to sample from each table.
            ignore_tables (list, optional): A list of table names to exclude.

        Returns:
            str: A formatted string with sample data, or None if an error occurs.
        """
        if self.conn is None:
            print("Not connected to a database.")
            return None

        if ignore_tables is None:
            ignore_tables = []

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT tablename
                    FROM pg_catalog.pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY tablename;
                """)
                all_tables = [row[0] for row in cur.fetchall()]

            # Filter out the tables in the ignore list
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
                            formatted_row = [str(cell) if cell is not None else 'NULL' for cell in row]
                            output_text += ", ".join(formatted_row) + "\n"
                        
                        output_text += "\n"

                except psycopg2.Error as e:
                    output_text += f"[Could not retrieve samples for table {table_name}: {e}]\n\n"
                    self.conn.rollback()

            return output_text

        except psycopg2.Error as e:
            print(f"Error fetching table list: {e}")
            self.conn.rollback()
            return None