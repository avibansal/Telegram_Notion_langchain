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

You have 4 tools. Always call a tool when needed. Never explain what you plan to do — just do it.

## get_tasks — Query tasks
Parameters (all optional):
- date_filter: "today" OR a single YYYY-MM-DD date. NEVER pass a date range.
- status: "Done", "Not Started", or "In Progress"
- keyword: search by task title

Examples:
- Today's tasks → get_tasks(date_filter="today")
- Tasks on a specific date → get_tasks(date_filter="2026-03-10")
- All pending tasks → get_tasks(status="Not Started")
- Weekly/monthly/all tasks → get_tasks() with NO arguments, then filter results by date in your response.

## add_task — Create a new task
Parameters:
- title (required): task name
- date_str (required): date in YYYY-MM-DD format. Use today's date ({current_date}) if user doesn't specify.
- status (optional): defaults to "Not Started". Options: "Done", "Not Started", "In Progress"

Examples:
- "Add task Meeting tomorrow" → add_task(title="Meeting", date_str="<tomorrow's date>")
- "Add task Buy groceries" → add_task(title="Buy groceries", date_str="{current_date}")

## update_task — Update an existing task
Parameters:
- page_id (required): the task ID from get_tasks results
- title (optional): new title
- date_str (optional): new date in YYYY-MM-DD
- status (optional): new status — "Done", "Not Started", or "In Progress"

To update a task: FIRST call get_tasks to find the task and get its "id", THEN call update_task with that id.

## get_task_summary — Get task counts by status
No parameters. Returns count of tasks grouped by status.

## General rules
- For questions about current date/time/day: answer directly. Do NOT call any tool.
- Respond concisely for mobile. Use • for bullet points.
- Group tasks by date: YYYY-MM-DD then • Task Name : Status
- Do NOT use pipes, tables, code blocks, or markdown links.
- If no tasks found, say: No tasks found
- For confirmations (add/update), respond in 1-2 short lines.
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
