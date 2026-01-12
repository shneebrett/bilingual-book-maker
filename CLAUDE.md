# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

bilingual_book_maker 是一个 AI 翻译工具，使用 ChatGPT 等大语言模型将 epub/txt/srt 文件翻译成双语版本。该工具专为翻译进入公共领域的书籍设计。

## Core Architecture

### 模块结构

- **book_maker/loader/**: 负责加载不同格式的文件
  - `epub_loader.py`: EPUB 文件加载器
  - `txt_loader.py`: 文本文件加载器
  - `srt_loader.py`: 字幕文件加载器
  - `md_loader.py`: Markdown 文件加载器
  - `base_loader.py`: 所有加载器的基类

- **book_maker/translator/**: 实现各种翻译服务的适配器
  - `chatgptapi_translator.py`: OpenAI ChatGPT 翻译器
  - `claude_translator.py`: Anthropic Claude 翻译器
  - `gemini_translator.py`: Google Gemini 翻译器
  - `deepl_translator.py`: DeepL 翻译器
  - `google_translator.py`: Google Translate 翻译器
  - `qwen_translator.py`: 阿里云通义千问翻译器
  - `groq_translator.py`: Groq 翻译器
  - `xai_translator.py`: xAI 翻译器
  - `base_translator.py`: 所有翻译器的基类

- **book_maker/cli.py**: 命令行接口入口，处理所有参数解析
- **book_maker/utils.py**: 工具函数和常量定义
- **book_maker/config.py**: 配置文件

### 设计模式

- **策略模式**: 通过 `MODEL_DICT` 和 `BOOK_LOADER_DICT` 动态选择翻译器和加载器
- **模板方法**: 所有翻译器继承 `base_translator.py`，加载器继承 `base_loader.py`
- **依赖注入**: 通过构造函数注入 API 密钥、模型配置等

## Development Commands

### 安装依赖

```bash
# 使用 pip 安装
pip install -r requirements.txt

# 或使用 PDM（推荐）
pdm install
```

### 运行测试

```bash
# 运行集成测试
make tests
# 或直接使用 pytest
pytest tests/test_integration.py

# 运行特定测试
pytest tests/test_epub_metadata.py
```

### 代码格式化

```bash
# 使用 black 格式化代码（提交前必须运行）
make fmt
# 或直接使用 black
black .
```

### 运行翻译

```bash
# 基本用法（测试模式）
python make_book.py --book_name test_books/animal_farm.epub --openai_key ${openai_key} --test

# 完整翻译
python make_book.py --book_name test_books/animal_farm.epub --openai_key ${openai_key} --language zh-hans

# 使用不同模型
python make_book.py --book_name test_books/animal_farm.epub --model claude --claude_key ${claude_key}
python make_book.py --book_name test_books/animal_farm.epub --model gemini --gemini_key ${gemini_key}

# 并行处理（加速翻译）
python make_book.py --book_name test_books/animal_farm.epub --openai_key ${openai_key} --parallel-workers 4
```

### 构建和发布

```bash
# 使用 PDM 构建
pdm build

# 安装为命令行工具
pip install -e .
# 然后可以使用 bbook_maker 命令
bbook_maker --book_name test_books/animal_farm.epub --openai_key ${openai_key} --test
```

### Docker 使用

```bash
# 构建镜像
docker build --tag bilingual_book_maker .

# 运行容器（Linux）
docker run --rm --name bilingual_book_maker \
  --mount type=bind,source=/path/to/books,target='/app/test_books' \
  bilingual_book_maker \
  --book_name /app/test_books/animal_farm.epub \
  --openai_key ${openai_key} \
  --test
```

## Key Implementation Details

### 添加新的翻译器

1. 在 `book_maker/translator/` 创建新文件，继承 `BaseTranslator`
2. 实现 `translate()` 方法
3. 在 `book_maker/translator/__init__.py` 的 `MODEL_DICT` 中注册

### 添加新的文件格式支持

1. 在 `book_maker/loader/` 创建新文件，继承 `BaseLoader`
2. 实现必要的加载和保存方法
3. 在 `book_maker/loader/__init__.py` 的 `BOOK_LOADER_DICT` 中注册

### Prompt 自定义

支持三种方式自定义翻译提示词：
- 直接字符串: `--prompt "Translate {text} to {language}"`
- JSON 文件: `--prompt prompt_template.json`（包含 `user` 和 `system` 键）
- PromptDown 格式: `--prompt prompt.md`（支持 developer message）

必须包含 `{text}` 占位符，`{language}` 可选。

### 环境变量

可以通过环境变量设置 API 密钥，避免命令行暴露：
- `BBM_OPENAI_API_KEY`: OpenAI API 密钥
- `BBM_CLAUDE_API_KEY`: Claude API 密钥
- `BBM_GOOGLE_GEMINI_KEY`: Gemini API 密钥
- `BBM_CAIYUN_API_KEY`: 彩云翻译 API 密钥
- `BBM_DEEPL_API_KEY`: DeepL API 密钥
- `BBM_GROQ_API_KEY`: Groq API 密钥
- `BBM_XAI_API_KEY`: xAI API 密钥
- `BBM_QWEN_API_KEY`: 通义千问 API 密钥

### 翻译恢复机制

使用 `--resume` 参数可以在中断后恢复翻译，避免重复翻译已完成的部分。

### 并行处理

使用 `--parallel-workers` 参数可以并行处理 EPUB 的多个章节，显著提升翻译速度。建议值为 2-4。

## Testing

- 使用 `test_books/animal_farm.epub` 作为测试文件
- 使用 `--test` 参数只翻译前 10 段（可通过 `--test_num` 调整）
- 集成测试位于 `tests/test_integration.py`
- 元数据测试位于 `tests/test_epub_metadata.py`
