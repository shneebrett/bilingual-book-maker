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
