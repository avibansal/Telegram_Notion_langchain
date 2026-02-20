import json
import requests
from datetime import date
from langchain_core.tools import tool as langchain_tool

NOTION_TOKEN = os.getenv("NOTION_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")
IMAGE_DUMP_PAGE_ID = os.getenv("IMAGE_DUMP_PAGE_ID")
BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@langchain_tool
def get_tasks(date_filter=None, status=None, keyword=None):
    """
    Query tasks from the database.
    - date_filter: exact date string (YYYY-MM-DD), or "today"
    - status: filter by status name (e.g. "Done", "Not Started", "In Progress")
    - keyword: search tasks whose title contains this keyword
    """
    url = f"{BASE_URL}/databases/{DATABASE_ID}/query"

    filters = []

    if date_filter:
        if date_filter == "today":
            date_filter = date.today().isoformat()
        filters.append({
            "property": "Date",
            "date": {"equals": date_filter}
        })

    if status:
        filters.append({
            "property": "Status",
            "status": {"equals": status}
        })

    if keyword:
        filters.append({
            "property": "Task",
            "rich_text": {"contains": keyword}
        })

    payload = {}
    if len(filters) == 1:
        payload["filter"] = filters[0]
    elif len(filters) > 1:
        payload["filter"] = {"and": filters}

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(response.text)

    tasks = []
    for page in response.json()["results"]:
        props = page["properties"]

        title = (
            props["Task"]["title"][0]["plain_text"]
            if props["Task"]["title"]
            else "Untitled"
        )

        status_prop = props.get("Status", {})
        if "status" in status_prop and status_prop["status"]:
            task_status = status_prop["status"]["name"]
        elif "select" in status_prop and status_prop["select"]:
            task_status = status_prop["select"]["name"]
        else:
            task_status = "No Status"

        date_value = (
            props["Date"]["date"]["start"]
            if props["Date"]["date"]
            else None
        )

        tasks.append({
            "id": page["id"],
            "task": title,
            "date": date_value,
            "status": task_status
        })

    return json.dumps(tasks) if tasks else "No tasks found."

@langchain_tool
def add_task(title, date_str, status="Not Started"):
    """Create a new task in the database."""
    url = f"{BASE_URL}/pages"

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Task": {
                "title": [{"text": {"content": title}}]
            },
            "Date": {
                "date": {"start": date_str}
            },
            "Status": {
                "status": {"name": status}
            }
        }
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()["id"]

@langchain_tool
def update_task(page_id, title=None, date_str=None, status=None):
    """Update any combination of title, date, or status for a task."""
    url = f"{BASE_URL}/pages/{page_id}"

    properties = {}

    if title:
        properties["Task"] = {
            "title": [{"text": {"content": title}}]
        }
    if date_str:
        properties["Date"] = {
            "date": {"start": date_str}
        }
    if status:
        properties["Status"] = {
            "status": {"name": status}
        }

    if not properties:
        return "Nothing to update"

    response = requests.patch(url, headers=HEADERS, json={"properties": properties})
    if response.status_code != 200:
        raise Exception(response.text)

    return "Updated successfully"

@langchain_tool
def get_task_summary():
    """Returns a count of tasks grouped by status."""
    result = get_tasks.invoke({})
    all_tasks = json.loads(result) if isinstance(result, str) and result != "No tasks found." else []
    summary = {}
    for task in all_tasks:
        s = task["status"]
        summary[s] = summary.get(s, 0) + 1
    return json.dumps(summary) if summary else "No tasks found."

@langchain_tool
def dump_image(image_url: str, caption: str = "") -> str:
    """Save an image to the Notion Images Dump database. Requires image_url and optional caption."""
    url = f"{BASE_URL}/pages"
    today = date.today().isoformat()

    payload = {
        "parent": {"database_id": IMAGE_DUMP_PAGE_ID},
        "properties": {
            "Caption": {
                "title": [{"text": {"content": caption or "Untitled"}}]
            },
            "Files & media": {
                "files": [
                    {
                        "type": "external",
                        "name": caption or "image",
                        "external": {"url": image_url}
                    }
                ]
            },
            "Date": {
                "date": {"start": today}
            }
        }
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(response.text)

    return f"Image saved to Notion with caption: {caption}"
