"""Offer the fictional contact tools over MCP."""
from typing import Annotated
from fastmcp import FastMCP
from contacts import search_contacts as search, draft_connection_message as draft

mcp = FastMCP('Fictional contact assistant')


@mcp.tool
def search_contacts(
    field: Annotated[str, 'One of: name, company, job title, or interest.'],
    query: Annotated[str, 'Text to find in the chosen field.'],
) -> dict:
    """Search the fictional practice contacts; not real people or LinkedIn data."""
    return search(field, query)


@mcp.tool
def draft_connection_message(
    name: Annotated[str, 'The name of one fictional contact in the practice data.'],
) -> dict:
    """Prepare a connection message of at most 200 characters for a fictional contact."""
    return draft(name)


if __name__ == '__main__':
    mcp.run(transport='http', host='127.0.0.1', port=8001)
