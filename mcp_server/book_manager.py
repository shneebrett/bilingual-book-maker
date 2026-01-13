"""Book management for MCP server."""
import uuid
from typing import Dict, Optional
from book_maker.loader import BOOK_LOADER_DICT


class BookManager:
    """Manages loaded books and their state."""

    def __init__(self):
        self._books: Dict[str, dict] = {}

    def load_book(self, file_path: str, book_type: str = "epub") -> dict:
        """Load a book and return metadata."""
        book_id = str(uuid.uuid4())
        loader_class = BOOK_LOADER_DICT.get(book_type)
        if not loader_class:
            raise ValueError(f"Unsupported book type: {book_type}")

        loader = loader_class(file_path)

        self._books[book_id] = {
            "id": book_id,
            "path": file_path,
            "type": book_type,
            "loader": loader,
            "translations": {}
        }

        return {
            "success": True,
            "book_id": book_id,
            "title": getattr(loader, "title", "Unknown"),
            "language": getattr(loader, "language", "unknown"),
            "total_chapters": len(getattr(loader, "chapters", [])),
        }

    def get_book(self, book_id: str) -> Optional[dict]:
        """Get book by ID."""
        return self._books.get(book_id)


# Global instance
book_manager = BookManager()
