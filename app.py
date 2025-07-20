from dotenv import load_dotenv
from pydantic_ai.messages import ModelMessage
import chainlit as cl
from agents import agent

load_dotenv()

@cl.on_chat_start
async def start():
    cl.user_session.set("message_history", [])

@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")  # type: list[ModelMessage]

    # 2. Pass the current message history to the agent on each run
    result = await agent.run(message.content, message_history=message_history)

    # 3. Update the history with the messages from the completed run
    cl.user_session.set("message_history", result.all_messages())

    # Send the final answer
    await cl.Message(content=result.output).send()
    