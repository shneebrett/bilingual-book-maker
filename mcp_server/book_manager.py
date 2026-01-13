"""Book management for MCP server."""
import os
import uuid
from typing import Dict, Optional
from bs4 import BeautifulSoup
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

    def get_content(self, book_id: str, chapter_index: int, start: int = 0, count: int = 10) -> dict:
        """Get content from a specific chapter."""
        book = self.get_book(book_id)
        if not book:
            return {"success": False, "error": "Book not found"}

        loader = book["loader"]
        chapters = getattr(loader, "chapters", [])

        if chapter_index >= len(chapters):
            return {"success": False, "error": "Chapter index out of range"}

        chapter = chapters[chapter_index]
        paragraphs = getattr(chapter, "paragraphs", [])

        end = min(start + count, len(paragraphs))
        selected = paragraphs[start:end]

        return {
            "success": True,
            "chapter_index": chapter_index,
            "chapter_title": getattr(chapter, "title", f"Chapter {chapter_index}"),
            "paragraphs": [
                {
                    "index": start + i,
                    "text": p.get_text() if hasattr(p, "get_text") else str(p),
                    "html": str(p)
                }
                for i, p in enumerate(selected)
            ],
            "has_more": end < len(paragraphs)
        }

    def save_translation(self, book_id: str, chapter_index: int, translations: list) -> dict:
        """Save translations for a chapter."""
        book = self.get_book(book_id)
        if not book:
            return {"success": False, "error": "Book not found"}

        if chapter_index not in book["translations"]:
            book["translations"][chapter_index] = {}

        for trans in translations:
            idx = trans["index"]
            book["translations"][chapter_index][idx] = {
                "original": trans["original"],
                "translation": trans["translation"]
            }

        total_translated = sum(len(ch) for ch in book["translations"].values())
        loader = book["loader"]
        total_paragraphs = sum(
            len(getattr(ch, "paragraphs", []))
            for ch in getattr(loader, "chapters", [])
        )

        return {
            "success": True,
            "saved_count": len(translations),
            "progress_percentage": round(total_translated / total_paragraphs * 100, 2) if total_paragraphs > 0 else 0
        }

    def export_bilingual_book(self, book_id: str, output_path: str = None) -> dict:
        """Export bilingual book."""
        book = self.get_book(book_id)
        if not book:
            return {"success": False, "error": "Book not found"}

        loader = book["loader"]
        translations = book["translations"]

        # Apply translations to loader
        for chapter_idx, chapter_trans in translations.items():
            chapter = loader.chapters[chapter_idx]
            paragraphs = getattr(chapter, "paragraphs", [])

            for para_idx, trans_data in chapter_trans.items():
                if para_idx < len(paragraphs):
                    para = paragraphs[para_idx]
                    original_text = trans_data["original"]
                    translated_text = trans_data["translation"]

                    # Create bilingual paragraph
                    bilingual_html = f"{original_text}<br/><br/>{translated_text}"

                    # Update paragraph content
                    if hasattr(para, "string"):
                        para.string = bilingual_html
                    else:
                        soup = BeautifulSoup(bilingual_html, "html.parser")
                        para.clear()
                        para.append(soup)

        # Generate output path
        if not output_path:
            base, ext = os.path.splitext(book["path"])
            output_path = f"{base}_bilingual{ext}"

        # Save using loader's make_bilingual method
        loader.make_bilingual(output_path)

        file_size = os.path.getsize(output_path) / (1024 * 1024)

        return {
            "success": True,
            "output_path": output_path,
            "file_size": f"{file_size:.2f} MB"
        }


# Global instance
book_manager = BookManager()
