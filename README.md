# Telegram Notion Task Manager

This project is a Telegram bot that integrates with Notion using LangChain and Groq's LLM. It allows you to manage tasks in a Notion database directly from Telegram, using natural language.

## Features

- **Task Management**:
  - View tasks (filter by date, status, or keyword).
  - Add new tasks with natural language (e.g., "Add a meeting tomorrow at 10am").
  - Update tasks (e.g., "Mark the meeting as Done").
  - Get summaries of your tasks.
- **Image Handling**:
  - Send images to the bot, and they will be automatically saved to a specific Notion page (Image Dump).
- **Natural Language Interface**: Powered by Groq LLM (Llama 3) to understand your requests.

## Prerequisites

- Python 3.8 or higher.
- A Telegram Bot Token (from @BotFather).
- A Notion Integration Token (created at [Notion Developers](https://www.notion.so/my-integrations)).
- A Notion Database for tasks.
- A Notion Page for dumping images.
- A Groq API Key (from [Groq Console](https://console.groq.com/)).

### Notion Setup

1.  **Create an Integration**: Go to [Notion Developers](https://www.notion.so/my-integrations) and create a new integration. Copy the "Internal Integration Token".
2.  **Share Database**: Open your Tasks database in Notion, click the `...` menu, scroll to "Connections", and add your integration.
3.  **Share Page**: Do the same for the page where you want images to be saved.
4.  **Get IDs**:
    -   **Database ID**: Found in the URL of your database page (between the workspace name and the `?`).
    -   **Page ID**: Found in the URL of your image dump page.

## Installation

1.  Clone this repository:
    ```bash
    git clone <repository_url>
    cd Telegram_Notion_langchain
    ```

2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the root directory (or rename `.env.example` to `.env`):
    ```bash
    cp .env.example .env
    ```

2.  Open the `.env` file and fill in your credentials:
    ```ini
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
    NOTION_KEY=your_notion_integration_token_here
    DATABASE_ID=your_notion_database_id_here
    IMAGE_DUMP_PAGE_ID=your_notion_page_id_for_images_here
    GROQ_API_KEY=your_groq_api_key_here
    ```

## Usage

1.  Start the bot:
    ```bash
    python telegram_bot.py
    ```

2.  Open Telegram and find your bot.

3.  Send `/start` to see the welcome message.

4.  Interact with the bot using natural language:
    -   "What are my tasks for today?"
    -   "Add a task to buy groceries on Saturday."
    -   "Mark 'Buy groceries' as Done."
    -   "Show me a summary of my tasks."
    -   Send a photo to save it to your Notion page.

## Project Structure

-   `telegram_bot.py`: Main entry point for the Telegram bot. Handles message routing.
-   `llm.py`: Configures the LangChain agent and Groq LLM.
-   `tool.py`: Defines the tools for interacting with the Notion API (get tasks, add task, update task, dump image).
-   `mcp_test.py`: (Optional) Testing script for Model Context Protocol.
