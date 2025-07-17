from db import PostgresDB
from pydantic_ai import Agent
from dotenv import load_dotenv
from instrument import logfire
from pydantic_ai.messages import ModelMessage # Import for type hinting

load_dotenv()

agent = Agent(
    'google-gla:gemini-2.5-pro',
    system_prompt='Your task is Answer the user query if you need to run a SQL query first get the database schema and sample data.',
)

@agent.tool
def get_db_schema_and_sample_data(run_context):
    """Get the database schema and sample data."""
    ignore_tables = ["vectors"]
    db = PostgresDB()
    db.connect()
    sample_data = db.get_table_samples_as_text(ignore_tables=ignore_tables)
    schema_info = db.get_schema_as_text(ignore_tables=ignore_tables)

    if schema_info and sample_data:
        full_context_for_llm = schema_info + sample_data

    return full_context_for_llm

@agent.tool_plain
def run_sql_query(query: str) -> str:
    """
    Run a SQL query against the database and return the results.
    Args:
        query: The SQL query string to execute.
    """
    try:
        db = PostgresDB()
        db.connect()
        query_result = db.query(query)
        return query_result
    except Exception as e:
        return f"Error executing query: {e}. Please check your SQL syntax and table/column names."

def main():
    """
    Main function to run the interactive chat loop with the AI agent.
    """
    print("🤖 AI Database Agent is ready. Type 'exit' or 'quit' to end the session.")
    
    # 1. Initialize an empty list to store the conversation history
    message_history: list[ModelMessage] = []
    
    while True:
        # Get user input from the console
        user_query = input("> ")

        # Check for exit condition
        if user_query.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        # Run the agent with the user's query and print the output
        try:
            # 2. Pass the current message history to the agent on each run
            result = agent.run_sync(user_query, message_history=message_history)
            print(result.output)
            
            # 3. Update the history with the messages from the completed run
            message_history = result.all_messages()
            
        except Exception as e:
            # Catch potential errors during agent execution
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()