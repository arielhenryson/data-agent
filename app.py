import chainlit as cl
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types
from data_agent.agent import root_agent

# 1. Load environment variables
load_dotenv()

# 2. Instantiate the runner globally so it's created only once.
# This runner holds the agent's state and manages sessions.
runner = InMemoryRunner(
    agent=root_agent,
    app_name='data_agent_app',  # A name for your application
)

@cl.on_chat_start
async def start():
    """
    This function is called when a new chat session begins.
    It creates a new agent session and stores its ID.
    """
    # Create a new session using the runner's session service.
    # We use a default 'user' ID here, but you could use cl.user.id if you have authentication.
    session = await runner.session_service.create_session(
        app_name='data_agent_app', user_id='user'
    )

    # Store the unique session ID in the Chainlit user session.
    cl.user_session.set("session_id", session.id)

@cl.on_message
async def main(message: cl.Message):
    """
    This function is called for every new message from the user.
    """
    # 1. Retrieve the session ID for the current user.
    session_id = cl.user_session.get("session_id")

    # 2. Format the user's message into the required Content object.
    content = types.Content(
        role='user', parts=[types.Part.from_text(text=message.content)]
    )

    # 3. Create a placeholder message in the UI that we will stream the response into.
    msg = cl.Message(content="")
    await msg.send()

    # 4. Run the agent and stream the response.
    # The runner.run() method is an async generator that yields events.
    response_tokens = []
    async for event in runner.run_async(
        user_id='user',
        session_id=session_id,
        new_message=content,
    ):
        # Check for text content in the event and stream it.
        if event.content and event.content.parts and event.content.parts[0].text:
            token = event.content.parts[0].text
            await msg.stream_token(token)
            response_tokens.append(token)

    # 5. Finalize the message stream.
    await msg.update()