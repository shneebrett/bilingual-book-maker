"""FastMCP server for bilingual book maker."""
from mcp.server.fastmcp import FastMCP
from mcp_server.book_manager import book_manager

mcp = FastMCP("bilingual-book-mcp")


@mcp.tool()
def load_book(file_path: str, book_type: str = "epub") -> dict:
    """Load a book file and return metadata.

    Args:
        file_path: Path to the book file
        book_type: Type of book (epub, txt, srt, md)

    Returns:
        Book metadata including book_id, title, chapters count
    """
    try:
        return book_manager.load_book(file_path, book_type)
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp.run()
