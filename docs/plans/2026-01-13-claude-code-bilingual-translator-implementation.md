# Claude Code 双语翻译器实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 创建基于 MCP 的双语翻译工作流，使用 Claude Code 本身进行翻译，无需外部 API key。

**Architecture:** 分为三层：(1) MCP 服务器暴露现有项目的文件加载/保存功能，(2) Claude Code Skill 处理用户交互和翻译流程编排，(3) 复用现有 book_maker 模块处理文件格式。

**Tech Stack:** Python 3.8+, FastMCP, ebooklib, beautifulsoup4, Markdown (Skill 定义)

---

## 阶段 1：MCP 服务器核心功能

### Task 1: 创建 MCP 服务器基础结构

**Files:**
- Create: `mcp_server/__init__.py`
- Create: `mcp_server/server.py`
- Create: `mcp_server/book_manager.py`

**Step 1: 创建空的包结构**

创建 `mcp_server/__init__.py`:
```python
"""MCP Server for bilingual book maker."""
__version__ = "0.1.0"
```

**Step 2: 创建 book_manager 模块**

创建 `mcp_server/book_manager.py`:
```python
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
```

**Step 3: 创建 MCP 服务器主文件**

创建 `mcp_server/server.py`:
```python
"""FastMCP server for bilingual book maker."""
from mcp.server.fastmcp import FastMCP
from book_manager import book_manager

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
```

**Step 4: 测试基础结构**

运行服务器测试导入:
```bash
cd D:\bilingual_book_maker-main
python -c "from mcp_server.book_manager import book_manager; print('OK')"
```

Expected: 输出 "OK"

**Step 5: 提交**

```bash
git add mcp_server/
git commit -m "feat(mcp): 创建 MCP 服务器基础结构和 BookManager"
```

---

### Task 2: 实现 get_content 工具

**Files:**
- Modify: `mcp_server/book_manager.py`
- Modify: `mcp_server/server.py`

**Step 1: 在 BookManager 添加 get_content 方法**

在 `mcp_server/book_manager.py` 的 `BookManager` 类中添加:
```python
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
```

**Step 2: 在 MCP 服务器添加 get_content 工具**

在 `mcp_server/server.py` 添加:
```python
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
```

**Step 3: 提交**

```bash
git add mcp_server/
git commit -m "feat(mcp): 实现 get_content 工具获取章节内容"
```

---

### Task 3: 实现 save_translation 工具

**Files:**
- Modify: `mcp_server/book_manager.py`
- Modify: `mcp_server/server.py`

**Step 1: 在 BookManager 添加 save_translation 方法**

在 `mcp_server/book_manager.py` 的 `BookManager` 类中添加:
```python
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
```

**Step 2: 在 MCP 服务器添加 save_translation 工具**

在 `mcp_server/server.py` 添加:
```python
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
```

**Step 3: 提交**

```bash
git add mcp_server/
git commit -m "feat(mcp): 实现 save_translation 工具保存翻译结果"
```

---

### Task 4: 实现 export_bilingual_book 工具

**Files:**
- Modify: `mcp_server/book_manager.py`
- Modify: `mcp_server/server.py`

**Step 1: 在 BookManager 添加 export 方法**

在 `mcp_server/book_manager.py` 的 `BookManager` 类中添加:
```python
import os
from bs4 import BeautifulSoup


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
```

**Step 2: 在 MCP 服务器添加 export 工具**

在 `mcp_server/server.py` 添加:
```python
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
```

**Step 3: 提交**

```bash
git add mcp_server/
git commit -m "feat(mcp): 实现 export_bilingual_book 工具导出双语书籍"
```

---

### Task 5: 实现 get_progress 工具

**Files:**
- Modify: `mcp_server/book_manager.py`
- Modify: `mcp_server/server.py`

**Step 1: 在 BookManager 添加 get_progress 方法**

在 `mcp_server/book_manager.py` 的 `BookManager` 类中添加:
```python
from datetime import datetime


def get_progress(self, book_id: str) -> dict:
    """Get translation progress."""
    book = self.get_book(book_id)
    if not book:
        return {"success": False, "error": "Book not found"}

    loader = book["loader"]
    chapters = getattr(loader, "chapters", [])
    translations = book["translations"]

    total_paragraphs = sum(
        len(getattr(ch, "paragraphs", []))
        for ch in chapters
    )

    completed_paragraphs = sum(len(ch) for ch in translations.values())

    # Find current position
    current_chapter = 0
    current_paragraph = 0
    for ch_idx in sorted(translations.keys()):
        current_chapter = ch_idx
        current_paragraph = max(translations[ch_idx].keys()) + 1 if translations[ch_idx] else 0

    return {
        "success": True,
        "book_path": book["path"],
        "total_chapters": len(chapters),
        "current_chapter": current_chapter,
        "current_paragraph": current_paragraph,
        "completed_paragraphs": completed_paragraphs,
        "total_paragraphs": total_paragraphs,
        "progress_percentage": round(completed_paragraphs / total_paragraphs * 100, 2) if total_paragraphs > 0 else 0,
        "last_update_time": datetime.now().isoformat()
    }
```

**Step 2: 在 MCP 服务器添加 get_progress 工具**

在 `mcp_server/server.py` 添加:
```python
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
```

**Step 3: 提交**

```bash
git add mcp_server/
git commit -m "feat(mcp): 实现 get_progress 工具获取翻译进度"
```

---

### Task 6: 配置 MCP 服务器到 Claude Code

**Files:**
- Create: `mcp_server/README.md`
- Modify: `~/.claude/mcp_settings.json` (手动操作)

**Step 1: 创建 MCP 服务器文档**

创建 `mcp_server/README.md`:
```markdown
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
```

**Step 2: 安装依赖**

```bash
pip install mcp
```

Expected: 成功安装

**Step 3: 手动配置 MCP 设置**

提示用户：
```
请手动编辑 ~/.claude/mcp_settings.json，添加以下配置：

{
  "mcpServers": {
    "bilingual-book-mcp": {
      "command": "python",
      "args": ["D:/bilingual_book_maker-main/mcp_server/server.py"]
    }
  }
}
```

**Step 4: 提交**

```bash
git add mcp_server/README.md
git commit -m "docs(mcp): 添加 MCP 服务器配置文档"
```

---

## 阶段 2：Claude Code Skill 开发

### Task 7: 创建 Skill 基础结构

**Files:**
- Create: `~/.claude/skills/bilingual-translator/skill.md`
- Create: `~/.claude/skills/bilingual-translator/config.json`

**Step 1: 创建 Skill 定义文件**

创建 `~/.claude/skills/bilingual-translator/skill.md`:
```markdown
# Bilingual Translator Skill

Translate books using Claude Code's translation capabilities via MCP.

## Usage

```bash
/bilingual-translator --book <path> --language <lang> [options]
```

## Parameters

- `--book`: Book file path (required)
- `--language`: Target language (required)
- `--batch-size`: Paragraphs per batch (default: 10)
- `--review-interval`: Review every N batches (default: 5)
- `--resume`: Resume interrupted translation
- `--output`: Output file path
- `--chapters`: Chapter range (e.g., 1-3,5)

## Process

1. Load book using MCP `load_book` tool
2. For each batch:
   - Get content using `get_content`
   - Translate using Claude Code
   - Show results and ask for review
   - Save using `save_translation`
3. Export using `export_bilingual_book`

## Implementation

When invoked:

1. Parse arguments
2. If `--resume`, check for existing progress
3. Load book and show metadata
4. Ask user to confirm translation range
5. Start translation loop with review checkpoints
6. Export final bilingual book
```

**Step 2: 创建配置文件**

创建 `~/.claude/skills/bilingual-translator/config.json`:
```json
{
  "default_batch_size": 10,
  "default_review_interval": 5,
  "translation_prompt_template": "Translate the following text to {language}. Maintain the original tone and style:\n\n{text}",
  "auto_save_interval": 1,
  "max_retries": 3,
  "temp_dir": ".translation_cache"
}
```

**Step 3: 提交到项目文档**

在项目中创建 skill 模板副本:
```bash
mkdir -p docs/skills
cp ~/.claude/skills/bilingual-translator/skill.md docs/skills/
cp ~/.claude/skills/bilingual-translator/config.json docs/skills/
git add docs/skills/
git commit -m "docs(skill): 添加 bilingual-translator skill 定义"
```

---

## 阶段 3：测试和验证

### Task 8: 端到端测试

**Files:**
- Create: `tests/test_mcp_integration.py`

**Step 1: 创建集成测试**

创建 `tests/test_mcp_integration.py`:
```python
"""Integration tests for MCP server."""
import sys
sys.path.insert(0, "D:/bilingual_book_maker-main")

from mcp_server.book_manager import BookManager


def test_load_book():
    """Test loading a book."""
    manager = BookManager()
    result = manager.load_book("test_books/animal_farm.epub", "epub")

    assert result["success"] is True
    assert "book_id" in result
    assert result["total_chapters"] > 0
    print(f"✓ Loaded book: {result['title']}")


def test_get_content():
    """Test getting content."""
    manager = BookManager()
    load_result = manager.load_book("test_books/animal_farm.epub", "epub")
    book_id = load_result["book_id"]

    content = manager.get_content(book_id, 0, 0, 5)

    assert content["success"] is True
    assert len(content["paragraphs"]) > 0
    print(f"✓ Got {len(content['paragraphs'])} paragraphs")


def test_save_and_progress():
    """Test saving translations and checking progress."""
    manager = BookManager()
    load_result = manager.load_book("test_books/animal_farm.epub", "epub")
    book_id = load_result["book_id"]

    translations = [
        {"index": 0, "original": "Test", "translation": "测试"}
    ]

    save_result = manager.save_translation(book_id, 0, translations)
    assert save_result["success"] is True

    progress = manager.get_progress(book_id)
    assert progress["completed_paragraphs"] == 1
    print(f"✓ Progress: {progress['progress_percentage']}%")


if __name__ == "__main__":
    test_load_book()
    test_get_content()
    test_save_and_progress()
    print("\n✅ All tests passed!")
```

**Step 2: 运行测试**

```bash
python tests/test_mcp_integration.py
```

Expected: 所有测试通过

**Step 3: 提交**

```bash
git add tests/test_mcp_integration.py
git commit -m "test(mcp): 添加 MCP 服务器集成测试"
```

---

## 完成检查清单

- [ ] MCP 服务器所有 5 个工具实现完成
- [ ] MCP 服务器配置到 Claude Code
- [ ] Skill 定义文件创建完成
- [ ] 集成测试通过
- [ ] 文档完善

## 下一步

完成此计划后，可以：
1. 在 Claude Code 中测试 `/bilingual-translator` 命令
2. 使用 `test_books/animal_farm.epub` 进行实际翻译测试
3. 根据使用反馈优化交互流程

---

**计划创建时间：** 2026-01-13
