# AI client compatibility

AgroDigital-AI has one shared open core. An AI can use the repository instructions as context if it can read GitHub files. To execute deterministic tools directly, the client needs a compatible execution environment or an MCP connection.

## Repository-only mode
1. Provide the repository URL and ask the assistant to read SKILL.md and docs/AI_AGENT_GUIDE.md.
2. Attach the image or data file to the AI conversation.
3. Ask it to state which evidence it can inspect and whether it can execute the requested operations.
4. If it cannot run the tools, it must provide an evidence-aware plan and not claim that processing occurred.

## MCP mode
Connect the optional local MCP server using examples/mcp-config.json. Install the full dependencies with:

~~~bash
python -m pip install -e ".[full]"
~~~

The client and MCP server must share access to files used by geospatial tools. A file attached only to a remote chat may not exist on the MCP server's filesystem. The AI may still visually interpret an attached ordinary image if its client supports vision; the server handles structured geospatial operations.

## What is not guaranteed
The repository does not install a native Skill in a chat product, enable MCP automatically, host a remote server, guarantee live data access, or guarantee that every AI client supports MCP. Model quality, file handling, context limits and execution capabilities vary by client and session. MCP compatibility is not universal AI compatibility.
