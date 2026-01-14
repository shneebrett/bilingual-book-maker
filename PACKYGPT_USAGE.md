# PackyGPT 翻译器使用指南

## 功能说明

PackyGPT 翻译器已成功集成到 bilingual_book_maker 项目中，支持使用 PackyAPI 的 GPT 模型（包括 GPT-5.1）进行书籍翻译。

## 使用方法

### 基础用法

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model packygpt \
  --packygpt_key YOUR_API_KEY \
  --test --test_num 2
```

### 使用 gpt51 别名

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model gpt51 \
  --packygpt_key YOUR_API_KEY \
  --test --test_num 2
```

### 指定具体模型

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model packygpt \
  --packygpt_key YOUR_API_KEY \
  --model_list gpt-5.1 \
  --test --test_num 2
```

### 完整翻译（不使用测试模式）

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model packygpt \
  --packygpt_key YOUR_API_KEY \
  --language zh-hans
```

### 使用环境变量

```bash
# 设置环境变量
export BBM_PACKYGPT_API_KEY=YOUR_API_KEY

# 运行翻译
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --model packygpt \
  --test --test_num 2
```

## 参数说明

### 必需参数

- `--book_name`: 要翻译的书籍文件路径
- `--model`: 使用 `packygpt` 或 `gpt51`
- `--packygpt_key`: PackyAPI 的 API 密钥（或使用环境变量 `BBM_PACKYGPT_API_KEY`）

### 可选参数

- `--model_list`: 指定具体模型名称（如 `gpt-5.1`, `gpt-4o` 等）
- `--language`: 目标语言（默认 `zh-hans`）
- `--test`: 测试模式，只翻译部分内容
- `--test_num`: 测试模式下翻译的段落数量（默认 10）
- `--temperature`: 翻译温度（默认 0.3）
- `--interval`: 请求间隔秒数（默认 1）
- `--prompt`: 自定义翻译提示词
- `--parallel-workers`: 并行处理的工作线程数

## 支持的模型

PackyGPT 翻译器支持 PackyAPI 提供的所有 OpenAI 兼容模型，包括但不限于：

- gpt-5.1
- gpt-4o
- gpt-4-turbo
- gpt-3.5-turbo

使用 `--model_list` 参数指定具体模型。

## 环境变量

- `BBM_PACKYGPT_API_KEY`: PackyGPT API 密钥
- `BBM_PACKYGPT_USER_MSG_TEMPLATE`: 自定义用户消息模板
- `BBM_PACKYGPT_SYS_MSG`: 自定义系统消息

## 实现细节

### 修改的文件

1. **book_maker/translator/packygpt_translator.py** (新建)
   - 基于 requests 库实现
   - 使用 OpenAI 兼容的 API 格式
   - 支持自动重试和错误处理

2. **book_maker/translator/__init__.py**
   - 导入 PackyGPT 翻译器
   - 注册 `packygpt` 和 `gpt51` 模型

3. **book_maker/cli.py**
   - 添加 `--packygpt_key` 命令行参数
   - 添加 API Key 处理逻辑
   - 添加模型配置支持

### 技术特性

- ✅ 使用 requests 库，避免 OpenAI 客户端兼容性问题
- ✅ 支持自动重试（最多 3 次）
- ✅ 支持指数退避策略
- ✅ 支持多 API Key 轮换
- ✅ 支持自定义提示词
- ✅ 支持温度和间隔配置

## 测试结果

### 测试环境
- 模型: gpt-5.1-2025-11-13
- 测试文件: Animal Farm (前 2 段)
- 翻译质量: ✅ 优秀
- 平均速度: ~1.7 秒/段

### 测试命令
```bash
# 测试 packygpt 模型
python make_book.py --book_name test_books/animal_farm.epub \
  --model packygpt --packygpt_key YOUR_KEY --test --test_num 2

# 测试 gpt51 别名
python make_book.py --book_name test_books/animal_farm.epub \
  --model gpt51 --packygpt_key YOUR_KEY --test --test_num 2

# 测试 model_list 参数
python make_book.py --book_name test_books/animal_farm.epub \
  --model packygpt --packygpt_key YOUR_KEY \
  --model_list gpt-5.1 --test --test_num 2
```

所有测试均通过 ✅

## 故障排除

### 问题：API Key 错误
```
Exception: Please provide PackyGPT API key
```
**解决方案**: 确保提供了 `--packygpt_key` 参数或设置了 `BBM_PACKYGPT_API_KEY` 环境变量

### 问题：请求被阻止
```
API error 403: Your request was blocked
```
**解决方案**: 这是正常的，PackyGPT 翻译器使用 requests 库可以正常工作

### 问题：翻译失败
```
Translation failed after 3 attempts
```
**解决方案**:
1. 检查网络连接
2. 检查 API Key 是否有效
3. 检查 API 配额是否充足
4. 增加 `--interval` 参数值

## 与其他翻译器的对比

| 特性 | PackyGPT | ChatGPTAPI | Gemini |
|------|----------|------------|--------|
| API 格式 | OpenAI 兼容 | OpenAI 官方 | Gemini 原生 |
| 实现方式 | requests | openai 库 | requests |
| 稳定性 | ✅ 高 | ⚠️ 中等 | ✅ 高 |
| 速度 | ✅ 快 | ✅ 快 | ✅ 快 |
| 成本 | 取决于 PackyAPI | 取决于 OpenAI | 取决于 Google |

## 相关文档

- [GPT-5.1 测试报告](GPT51_TEST_REPORT.md)
- [实现清单](IMPLEMENTATION_CHECKLIST.md)
- [项目 README](README.md)

## API Key 获取

访问 [PackyAPI](https://www.packyapi.com) 获取 API 密钥。
