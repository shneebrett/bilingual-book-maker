"""Simplified EPUB loader for MCP server."""
from ebooklib import epub
from bs4 import BeautifulSoup


class Chapter:
    """Represents a chapter in the book."""
    def __init__(self, title, paragraphs):
        self.title = title
        self.paragraphs = paragraphs


class SimplifiedEPUBLoader:
    """Simplified EPUB loader that only loads structure, no translation."""

    def __init__(self, epub_path):
        self.epub_path = epub_path
        self.book = epub.read_epub(epub_path)
        self.title = self._get_title()
        self.language = self._get_language()
        self.chapters = self._load_chapters()

    def _get_title(self):
        """Get book title."""
        title = self.book.get_metadata('DC', 'title')
        return title[0][0] if title else "Unknown"

    def _get_language(self):
        """Get book language."""
        lang = self.book.get_metadata('DC', 'language')
        return lang[0][0] if lang else "unknown"

    def _load_chapters(self):
        """Load all chapters and their paragraphs."""
        chapters = []
        items = list(self.book.get_items_of_type(9))  # 9 = ITEM_DOCUMENT

        for item in items:
            content = item.get_content()
            soup = BeautifulSoup(content, 'html.parser')

            # Extract title
            title_tag = soup.find(['h1', 'h2', 'h3', 'title'])
            title = title_tag.get_text() if title_tag else f"Chapter {len(chapters)}"

            # Extract paragraphs
            paragraphs = soup.find_all('p')

            if paragraphs:  # Only add chapters with content
                chapters.append(Chapter(title, paragraphs))

        return chapters

    def make_bilingual(self, output_path):
        """Save the book with bilingual content."""
        # Write the modified book
        epub.write_epub(output_path, self.book, {})
