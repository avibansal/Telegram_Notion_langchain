import json
import base64
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from tool import get_tasks, add_task, update_task, get_task_summary, dump_image

from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """You are a Notion Task Manager assistant connected to Telegram.

Format ALL responses in Telegram MarkdownV2-safe format:
Use bold for headings and dates
Group tasks by date

Display format:
YYYY-MM-DD
• Task Name : Completed
• Task Name : Pending
Do NOT use pipes , tables, code blocks, or links
Use • for bullet points only
Capitalize status as Completed or Pending inside parentheses
Keep responses concise and readable on mobile
Use emojis sparingly for clarity
If no tasks found, clearly say: No tasks found
For confirmations, respond in 1–2 short lines only
If user sends an image, describe what you see and help accordingly.
"""

llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=GROQ_API_KEY,
    temperature=0,
    max_tokens=512,
    max_retries=2,
)

agent = create_agent(
    model=llm,
    tools=[get_tasks, add_task, update_task, get_task_summary],
    system_prompt=SYSTEM_PROMPT,
)


def run_agent(user_message: str, image_base64: str = None) -> str:
    """Invoke the agent with a user message and optional image."""
    if image_base64:
        # Multimodal message with image + text
        content = [
            {"type": "text", "text": user_message or "What do you see in this image?"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            },
        ]
    else:
        content = user_message

    result = agent.invoke({"messages": [HumanMessage(content=content)]})
    # Search backwards for the last AI message with actual text content
    for msg in reversed(result["messages"]):
        if hasattr(msg, "type") and msg.type == "ai" and msg.content:
            return msg.content
    return "Sorry, I could not process that request."


# Run directly for quick testing
if __name__ == "__main__":
    response = run_agent("What is today's task list?")
    print(response)
