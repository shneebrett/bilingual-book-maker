# Bilingual Book Maker

The bilingual_book_maker is an AI translation tool that uses ChatGPT to assist users in creating multi-language versions of epub/txt/srt files and books. This tool is exclusively designed for translating epub books that have entered the public domain and is not intended for copyrighted works. 

## Features

- Translate epub, txt, and srt files to multiple languages
- Support for various AI models including GPT-4, GPT-3.5, Claude, Gemini, and more
- Bilingual output with original and translated text
- Parallel processing for faster translation
- Customizable prompts and translation options

## Supported Models

- OpenAI: gpt-5-mini, gpt-4, gpt-3.5-turbo
- Anthropic: claude-2, claude-3
- Google: gemini, geminipro
- Meta: llama-2, llama-3
- Amazon: bedrock
- Alibaba: qwen-mt-turbo, qwen-mt-plus
- And many more through LiteLLM support

## Installation

```bash
pip install -r requirements.txt
```

Or install via pip:

```bash
pip install -U bbook_maker
```

## Quick Start

```bash
python3 make_book.py --book_name test_books/animal_farm.epub --openai_key ${openai_key} --test
```

Or using the installed package:

```bash
bbook --book_name test_books/animal_farm.epub --openai_key ${openai_key} --test
```

## Usage Examples

### Basic Translation
```bash
python3 make_book.py --book_name test_books/animal_farm.epub --openai_key ${openai_key} --language "Simplified Chinese"
```

### Using Different Models
```bash
# Using Gemini
python3 make_book.py --book_name test_books/animal_farm.epub --gemini_key ${gemini_key} --model gemini

# Using Claude
python3 make_book.py --book_name test_books/animal_farm.epub --model claude --claude_key ${claude_key}

# Using DeepL
python3 make_book.py --book_name test_books/animal_farm.epub --model deepl --deepl_key ${deepl_key}
```

### Advanced Options
```bash
# Parallel processing
python3 make_book.py --book_name test_books/animal_farm.epub --openai_key ${openai_key} --parallel-workers 4

# Custom tags to translate
python3 make_book.py --book_name test_books/animal_farm.epub --translate-tags h1,h2,h3,p,div

# Custom prompt
python3 make_book.py --book_name test_books/animal_farm.epub --prompt "Translate {text} to {language}. Maintain the original meaning and context."
```

## Configuration Options

- `--book_name`: Path to the input book file
- `--language`: Target language for translation
- `--model`: AI model to use for translation
- `--openai_key`: OpenAI API key
- `--test`: Test mode (limited translation)
- `--proxy`: Proxy server for internet access
- `--resume`: Resume interrupted translation
- `--translate-tags`: HTML tags to translate (for epub files)
- `--batch_size`: Number of lines for batch translation (for txt files)
- `--parallel-workers`: Number of parallel workers for chapter processing

## Docker Usage

```bash
# Build image
docker build --tag bilingual_book_maker .

# Run container
docker run --rm --name bilingual_book_maker --mount type=bind,source=${folder_path},target='/app/test_books' bilingual_book_maker --book_name "/app/test_books/${book_name}" --openai_key ${openai_key} --language ${language}
```

## Contributing

Any issues or PRs are welcome. Please run `black make_book.py` before submitting the code.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is designed for translating epub books that have entered the public domain and is not intended for copyrighted works. Please review the project's disclaimer before using this tool.