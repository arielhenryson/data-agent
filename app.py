from db import PostgresDB

def main():
    ignore_tables = ["vectors"]
    db = PostgresDB()
    db.connect()
    sample_data = db.get_table_samples_as_text(ignore_tables=ignore_tables)
    schema_info = db.get_schema_as_text(ignore_tables=ignore_tables)

    # 4. Combine them for the full context
    if schema_info and sample_data:
        full_context_for_llm = schema_info + sample_data
        print(full_context_for_llm)
    db.disconnect()

if __name__ == "__main__":
    main()