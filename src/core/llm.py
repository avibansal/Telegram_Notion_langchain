import json
import base64
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from core.langchain_tool import get_tasks, add_task, update_task, get_task_summary, dump_image
import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def get_system_prompt():
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.now().strftime("%A")
    return f"""You are a Notion Task Manager assistant connected to Telegram.

Today's date is {current_date} ({current_day}).

TOOL USAGE RULES (follow strictly):
1. get_tasks date_filter only accepts "today" or a single YYYY-MM-DD date. NEVER pass date ranges.
2. To get this week/this month/all tasks: call get_tasks() with NO arguments. It returns all tasks. Then you filter the results by date in your response.
3. For questions about current date/time/day: answer directly from the date above. Do NOT call any tool.
4. Always call a tool when you can. Do NOT explain what you would do — just do it.

Response format rules:
• Keep responses concise and mobile-friendly
• Use • for bullet points, group tasks by date
• Format: YYYY-MM-DD then • Task Name : Status
• Do NOT use pipes, tables, code blocks, or links
• If no tasks found, say: No tasks found
"""

llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=GROQ_API_KEY,
    temperature=0,
    max_tokens=512,
    max_retries=2,
)


def run_agent(user_message: str, image_base64: str = None) -> str:
    """Invoke the agent with a user message and optional image."""
    # Create agent with fresh system prompt so it always knows today's date
    agent = create_agent(
        model=llm,
        tools=[get_tasks, add_task, update_task, get_task_summary],
        system_prompt=get_system_prompt(),
    )

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
