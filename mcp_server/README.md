# Bilingual Book MCP Server

MCP server for bilingual book maker.

## Installation

```bash
pip install mcp
```

## Configuration

Add to `~/.claude/mcp_settings.json`:

```json
{
  "mcpServers": {
    "bilingual-book-mcp": {
      "command": "python",
      "args": ["D:/bilingual_book_maker-main/mcp_server/server.py"]
    }
  }
}
```

## Tools

- `load_book`: Load a book file
- `get_content`: Get chapter content
- `save_translation`: Save translations
- `export_bilingual_book`: Export bilingual book
- `get_progress`: Get translation progress
