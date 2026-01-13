"""Integration tests for MCP server."""
import sys
sys.path.insert(0, "D:/bilingual_book_maker-main/.worktrees/bilingual-translator-mcp")

from mcp_server.book_manager import BookManager


def test_load_book():
    """Test loading a book."""
    manager = BookManager()
    result = manager.load_book("D:/bilingual_book_maker-main/test_books/animal_farm.epub", "epub")

    assert result["success"] is True
    assert "book_id" in result
    assert result["total_chapters"] > 0
    print(f"[OK] Loaded book: {result['title']}")
    return result["book_id"]


def test_get_content():
    """Test getting content."""
    manager = BookManager()
    load_result = manager.load_book("D:/bilingual_book_maker-main/test_books/animal_farm.epub", "epub")
    book_id = load_result["book_id"]

    content = manager.get_content(book_id, 0, 0, 5)

    assert content["success"] is True
    assert len(content["paragraphs"]) > 0
    print(f"[OK] Got {len(content['paragraphs'])} paragraphs")
    return book_id


def test_save_and_progress():
    """Test saving translations and checking progress."""
    manager = BookManager()
    load_result = manager.load_book("D:/bilingual_book_maker-main/test_books/animal_farm.epub", "epub")
    book_id = load_result["book_id"]

    translations = [
        {"index": 0, "original": "Test", "translation": "测试"}
    ]

    save_result = manager.save_translation(book_id, 0, translations)
    assert save_result["success"] is True

    progress = manager.get_progress(book_id)
    assert progress["completed_paragraphs"] == 1
    print(f"[OK] Progress: {progress['progress_percentage']}%")


if __name__ == "__main__":
    test_load_book()
    test_get_content()
    test_save_and_progress()
    print("\n[SUCCESS] All tests passed!")
