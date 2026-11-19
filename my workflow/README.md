# My workflow: fictional networking contacts

This practice project searches fictional people and drafts LinkedIn connection requests. It does not connect to LinkedIn or send messages. The names, companies and interests are made up; do not treat them as real profiles.

## Files

- `contacts.csv`: a local snapshot of the fictional Google Sheet. Changes in the sheet do **not** automatically update this file.
- `contacts.py`: loads the data and implements search and a 200-character message template.
- `tool_call.py`: lets Groq choose which function to run in response to a question.
- `mcp_server.py`: offers the same functions to MCP clients.

The Google Sheet is [here](https://docs.google.com/spreadsheets/d/1_6E97ad-AL769jA2mepnh8_hTC6AsteQRDMN4npuCyE/edit). It starts private. By default, both programs read the local CSV, so no Google credentials or public sharing are needed.

## Try the tool-calling example

In PowerShell from the repository root:

```powershell
cd 'my workflow'
python tool_call.py 'Draft a LinkedIn connection request for Neel Verma.'
python tool_call.py 'Who works at PaperKite Learning?'
```

This uses the `GROQ_API_KEY` in the existing `.env` file in the repository root; keep it private. The draft is generated with a small template, not invented by the model, and its length is checked before it is returned. In this command-line example, the draft is printed directly so that a model rewrite cannot make it longer. An MCP client may choose to rewrite tool output, so check the final text before using it.

## Try the MCP server

Start this from `my workflow` and leave it running:

```powershell
python mcp_server.py
```

In a second PowerShell terminal:

```powershell
fastmcp list http://localhost:8001/mcp --input-schema
fastmcp call http://localhost:8001/mcp search_contacts field=company query=PaperKite
fastmcp call http://localhost:8001/mcp draft_connection_message name='Neel Verma'
```

Port 8001 is used to avoid the original course server's port 8000. If occupied, stop the other program or change the port.

## Use the Google Sheet instead of the local snapshot

The sample sheet is private by default. The CSV endpoint used here needs permission for the server to read the sheet without Google sign-in. **Only for fictional data**, you may choose to make the sheet accessible to anyone with its link, or publish it to the web. This makes its contents available to other people; never do this for private or real contact data. It may take time for permission changes to take effect.

After setting access yourself, opt in in each terminal before starting the program:

```powershell
$env:CONTACTS_SOURCE = 'google'
```

Use `$env:CONTACTS_SOURCE = 'local'` to return to the snapshot. For a hosted server, configure `CONTACTS_SOURCE=google` in its environment only after setting sheet access. This example does not support private Google authentication.

## Five questions to test

Observed with Groq on 19 November 2026; model tool choices may vary on later runs.

| Question | Should use a contact tool? | Observed |
|---|---|---|
| What does Aarav Mehta do? | Yes | Yes: `search_contacts` |
| Who works at PaperKite Learning? | Yes | Yes: `search_contacts` |
| Who is interested in multimodal AI? | Yes | Yes: `search_contacts` |
| Draft a LinkedIn connection request for Neel Verma. | Yes | Yes: `draft_connection_message` |
| What is machine learning? | No | No |

## Deploy on FastMCP Gateway

Commit and push this folder to GitHub first. Create a server using your fork and the entrypoint `my workflow/mcp_server.py:mcp`. If the Gateway cannot resolve a path with a space, rename the folder to `my_workflow` and use `my_workflow/mcp_server.py:mcp`. A deployed server using the default local snapshot needs no Groq API key; Groq is used only by `tool_call.py`.

Your current FastMCP plan requires authentication. Redeploying does not turn it off. Test the new server with its URL and sign in when prompted.

## Run the tests

```powershell
python -m unittest -v test_contacts
```
