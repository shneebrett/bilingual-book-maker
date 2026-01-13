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


@mcp.tool()
def get_content(book_id: str, chapter_index: int, start: int = 0, count: int = 10) -> dict:
    """Get content from a specific chapter.

    Args:
        book_id: Book ID from load_book
        chapter_index: Chapter index (0-based)
        start: Starting paragraph index
        count: Number of paragraphs to retrieve

    Returns:
        Chapter content with paragraphs
    """
    try:
        return book_manager.get_content(book_id, chapter_index, start, count)
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def save_translation(book_id: str, chapter_index: int, translations: list) -> dict:
    """Save translation results.

    Args:
        book_id: Book ID
        chapter_index: Chapter index
        translations: List of {index, original, translation}

    Returns:
        Save status and progress
    """
    try:
        return book_manager.save_translation(book_id, chapter_index, translations)
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def export_bilingual_book(book_id: str, output_path: str = None) -> dict:
    """Export the bilingual book.

    Args:
        book_id: Book ID
        output_path: Output file path (optional)

    Returns:
        Export status and file info
    """
    try:
        return book_manager.export_bilingual_book(book_id, output_path)
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_progress(book_id: str) -> dict:
    """Get translation progress.

    Args:
        book_id: Book ID

    Returns:
        Progress information
    """
    try:
        return book_manager.get_progress(book_id)
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp.run()
