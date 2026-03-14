import json
import requests
from datetime import date
import os
from dotenv import load_dotenv
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
IMAGE_DUMP_PAGE_ID = os.getenv("IMAGE_DUMP_PAGE_ID")
BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_tasks_logic(date_filter=None, status=None, keyword=None):
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

def add_task_logic(title, date_str, status="Not Started"):
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

def update_task_logic(page_id, title=None, date_str=None, status=None):
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

def get_task_summary_logic():
    result = get_tasks_logic()
    all_tasks = json.loads(result) if isinstance(result, str) and result != "No tasks found." else []
    summary = {}
    for task in all_tasks:
        s = task["status"]
        summary[s] = summary.get(s, 0) + 1
    return json.dumps(summary) if summary else "No tasks found."

def dump_image_logic(image_url: str, caption: str = "") -> str:
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
