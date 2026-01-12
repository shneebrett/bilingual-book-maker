# 快速开始指南

## 配置说明

本项目已配置好使用 Claude Sonnet 4.5 模型进行翻译。

### 1. 环境配置

项目根目录下的 `.env` 文件已包含必要的配置：
- Claude API Key 已配置
- 默认模型设置为 `claude-sonnet-4-5-20250929`

**重要提示**: `.env` 文件包含敏感信息，已被 `.gitignore` 排除，不会被提交到 git 仓库。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 快速测试

使用测试模式翻译示例书籍（只翻译前 10 段）：

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model claude-sonnet-4-5-20250929 \
  --language zh-hans \
  --test
```

### 4. 完整翻译

翻译整本书：

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model claude-sonnet-4-5-20250929 \
  --language zh-hans
```

### 5. 使用环境变量（推荐）

由于 `.env` 文件已配置，你可以直接使用环境变量：

```bash
# 在 Windows PowerShell 中
$env:BBM_CLAUDE_API_KEY = Get-Content .env | Select-String "BBM_CLAUDE_API_KEY" | ForEach-Object { $_.ToString().Split('=')[1] }

# 然后运行
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model claude-sonnet-4-5-20250929 \
  --language zh-hans \
  --test
```

或者在 Linux/Mac 中：

```bash
# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 然后运行
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model claude-sonnet-4-5-20250929 \
  --language zh-hans \
  --test
```

### 6. 常用参数

- `--test`: 测试模式，只翻译前 10 段
- `--test_num N`: 指定测试翻译的段落数
- `--language`: 目标语言（默认：zh-hans）
- `--temperature`: 温度参数（默认：1.0）
- `--use_context`: 使用上下文提升翻译连贯性
- `--parallel-workers N`: 并行处理章节（推荐 2-4）

### 7. 高级用法

#### 并行翻译（加速）

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model claude-sonnet-4-5-20250929 \
  --language zh-hans \
  --parallel-workers 4
```

#### 使用上下文提升连贯性

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model claude-sonnet-4-5-20250929 \
  --language zh-hans \
  --use_context
```

#### 自定义翻译提示词

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model claude-sonnet-4-5-20250929 \
  --language zh-hans \
  --prompt "请将以下文本翻译成{language}，保持原文的风格和语气：\n{text}"
```

## 输出文件

- 成功完成：`{book_name}_bilingual.epub`
- 中断后临时文件：`{book_name}_bilingual_temp.epub`

## 恢复中断的翻译

如果翻译过程中断，可以使用 `--resume` 参数继续：

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model claude-sonnet-4-5-20250929 \
  --language zh-hans \
  --resume
```

## 安全提示

- **不要将 `.env` 文件提交到公共仓库**
- **不要在命令行中直接暴露 API key**
- 使用环境变量或 `.env` 文件管理敏感信息
- 定期轮换 API keys

## 支持的语言

运行以下命令查看所有支持的语言：

```bash
python make_book.py --help
```

常用语言代码：
- `zh-hans`: 简体中文
- `zh-hant`: 繁体中文
- `ja`: 日语
- `en`: 英语
- `fr`: 法语
- `de`: 德语
- `es`: 西班牙语

## 故障排除

### API 限流

如果遇到 API 限流，可以：
1. 降低并行工作数：`--parallel-workers 1`
2. 使用多个 API keys（用逗号分隔）
3. 等待一段时间后使用 `--resume` 继续

### 翻译质量

提升翻译质量的方法：
1. 使用 `--use_context` 保持上下文连贯性
2. 调整 `--temperature` 参数（0.7-1.0）
3. 自定义 `--prompt` 提示词
4. 使用更高级的模型

## 更多信息

详细文档请参考：
- [README.md](README.md) - 完整功能说明
- [README-CN.md](README-CN.md) - 中文文档
- [CLAUDE.md](CLAUDE.md) - 开发者指南
