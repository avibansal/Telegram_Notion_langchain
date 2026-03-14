import json
from langchain_core.tools import tool as langchain_tool
import os
from utils.utils import get_tasks_logic, add_task_logic, update_task_logic, get_task_summary_logic, dump_image_logic


@langchain_tool
def get_tasks(date_filter=None, status=None, keyword=None):
    """
    Query tasks from the database.
    - date_filter: exact date string (YYYY-MM-DD), or "today"
    - status: filter by status name (e.g. "Done", "Not Started", "In Progress")
    - keyword: search tasks whose title contains this keyword
    """
    return get_tasks_logic(date_filter, status, keyword)

@langchain_tool
def add_task(title, date_str, status="Not Started"):
    """Create a new task in the database."""
    return add_task_logic(title, date_str, status)

@langchain_tool
def update_task(page_id, title=None, date_str=None, status=None):
    """Update any combination of title, date, or status for a task."""
    return update_task_logic(page_id, title, date_str, status)

@langchain_tool
def get_task_summary():
    """Returns a count of tasks grouped by status."""
    return get_task_summary_logic()

@langchain_tool
def dump_image(image_url: str, caption: str = "") -> str:
    """Save an image to the Notion Images Dump database. Requires image_url and optional caption."""
    return dump_image_logic(image_url, caption)
