# Contacts MCP practice plan

**Goal:** Search the fictional contacts and draft a connection request of at most 200 characters.

**Approach:** Keep an offline copy of the Google Sheet's fictional rows for a working default. Offer an opt-in Google Sheet CSV source, since the current Sheet is private. Share the lookup and drafting functions between a FastMCP server and a Groq tool-calling example.

1. Add tests for searching by name, company and interest, errors, and message length.
2. Implement the contact data source, tool functions, MCP server and Groq tool loop.
3. Document local use, live-sheet access, deployment and five practice questions. Run the tests and exercise the server locally.
