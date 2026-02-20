import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()

NOTION_KEY = os.getenv("NOTION_TOKEN")
async def main():
    client = MultiServerMCPClient(
        {
            "notion": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@notionhq/notion-mcp-server"],
                "env": {
                    "OPENAPI_MCP_HEADERS": f'{{"Authorization": "Bearer {NOTION_KEY}", "Notion-Version": "2022-06-28"}}'
                },
            }
        }
    )

    tools = await client.get_tools()
    print("Connected Successfully!")
    print(f"Loaded {len(tools)} tools")

    notion_agent_instructions = """You are a Notion MCP execution agent.
You must use MCP tools to perform all workspace actions.
Never fabricate content. Never guess IDs.
If user intent requires multiple steps, execute them sequentially."""

    llm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=os.getenv("GROQ_API_KEY"),
    )

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=notion_agent_instructions,
    )

    result = await agent.ainvoke(
        {"messages": [HumanMessage(content="What is the name of the workspace?")]}
    )

    # Print only the final AI response
    for msg in result["messages"]:
        if hasattr(msg, "type") and msg.type == "ai" and msg.content:
            print(msg.content)


asyncio.run(main())
