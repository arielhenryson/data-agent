import sqlite3
import os

# Define the name for your SQLite database file
DB_FILE = "mydatabase.db"
# Define the path to your SQL schema file
SCHEMA_FILE = os.path.join("sql", "schema.sql")

def populate_db():
    """
    Connects to an SQLite database, creates the schema from an SQL file,
    and populates it.
    """
    # Check if the database file already exists. If so, you might want to delete it
    # to start with a fresh database each time the script is run.
    if os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' already exists. Removing it to start fresh.")
        os.remove(DB_FILE)

    conn = None
    try:
        # sqlite3.connect() will create the database file if it doesn't exist.
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        print(f"Connected to SQLite database: {DB_FILE}")

        # Read the schema from the .sql file
        print(f"Reading schema from '{SCHEMA_FILE}'...")
        with open(SCHEMA_FILE, "r") as f:
            sql_script = f.read()

        # Use executescript() to run multiple SQL statements at once
        cur.executescript(sql_script)
        print("Successfully executed SQL script.")

        # Commit the changes to the database
        conn.commit()
        print("Database populated successfully.")

    except sqlite3.Error as error:
        # More specific error handling for SQLite
        print(f"Error while populating SQLite database: {error}")

    except FileNotFoundError:
        print(f"Error: The schema file was not found at '{SCHEMA_FILE}'. Please check the path.")

    except Exception as error:
        print(f"An unexpected error occurred: {error}")

    finally:
        # Ensure the connection is closed even if an error occurs
        if conn is not None:
            conn.close()
            print("SQLite connection closed.")

if __name__ == "__main__":
    # Ensure the 'sql' directory exists before running
    if not os.path.isdir("sql"):
        print("Error: 'sql' directory not found. Please create it and add your schema.sql file.")
    else:
        populate_db()
