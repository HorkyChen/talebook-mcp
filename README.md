# Talebook MCP Server

A simple Model Context Protocol (MCP) server built with FastAPI that provides book-related tools.

## Features

- **get_books_count**: Returns the current count of books in the collection (defaults to 1)
- Built with FastAPI for both MCP and HTTP interfaces
- Supports both stdio transport (for MCP clients) and HTTP endpoints

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running as MCP Server (stdio transport)

```bash
python src/server.py
```

### Running as FastAPI HTTP Server

```bash
python src/server.py --fastapi
```

The HTTP server will be available at `http://localhost:8000`

### Available Endpoints (HTTP mode)

- `GET /` - Health check
- `GET /tools` - List available tools
- `POST /tools/get_books_count` - Get books count

### Available Tools (MCP mode)

- **get_books_count**: Get the current count of books in the collection
  - Input: No parameters required
  - Output: Text content with the books count

## MCP Configuration

To use this server with an MCP client, add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "talebook-mcp": {
      "command": "python",
      "args": ["/path/to/talebook-mcp/src/server.py"],
      "env": {}
    }
  }
}
```

## Development

The server is structured to be easily extensible. To add new tools:

1. Add the tool definition to the `list_tools()` function
2. Add the tool handler to the `call_tool()` function
3. Implement the tool function
4. Optionally add HTTP endpoints for the new tool

## Example Tool Usage

When using an MCP client, you can call the `get_books_count` tool:

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_books_count",
    "arguments": {}
  }
}
```

The server will respond with:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Current books count: 1"
    }
  ]
}
```
