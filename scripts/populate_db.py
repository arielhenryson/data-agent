
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def populate_db():
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        with open("sql/schema.sql", "r") as f:
            cur.execute(f.read())
        conn.commit()
        print("Database populated successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    populate_db()
