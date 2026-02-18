from dotenv import load_dotenv
load_dotenv()

from agents.pdf_agent import ask_policy
from agents.sql_agent import ask_customer

# Minimal MCP example (common pattern in FastMCP-style servers)
try:
    from mcp.server.fastmcp import FastMCP
except Exception as e:
    raise RuntimeError(
        "Your installed `mcp` package doesn't expose FastMCP at mcp.server.fastmcp. "
        "Share the exact error and I’ll adapt it to your MCP version."
    )

mcp = FastMCP("tcs-genai-multi-agent")

@mcp.tool()
def policy_search(question: str) -> str:
    """Answer policy questions using PDF RAG (Pinecone)."""
    return ask_policy(question)

@mcp.tool()
def customer_lookup(question: str) -> str:
    """Answer customer/ticket questions using SQLite."""
    return ask_customer(question)

if __name__ == "__main__":
    mcp.run()
