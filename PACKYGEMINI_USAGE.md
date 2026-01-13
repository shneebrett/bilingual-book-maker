# PackyGemini 翻译器使用说明

## 概述

PackyGemini 是为 PackyAPI 中转站定制的 Gemini 翻译器，使用 Gemini 原生 API 格式进行翻译。

## 为什么需要自定义翻译器

1. **Google SDK 不兼容**：官方 `google.generativeai` SDK 无法连接到 PackyAPI 中转站
2. **API 格式要求**：PackyAPI 的某些 API 密钥只支持 Gemini 原生格式（`/v1beta/models/{model}:generateContent`）
3. **直接 HTTP 请求**：使用 `requests` 库直接调用 API 端点，绕过 SDK 限制

## 技术实现

- **文件位置**：`book_maker/translator/packy_gemini_translator.py`
- **请求格式**：Gemini 原生 API 格式
- **认证方式**：使用 `x-goog-api-key` 请求头
- **端点格式**：`{api_base}/v1beta/models/{model}:generateContent`

## 使用方法

### 基本命令

```bash
python make_book.py \
  --book_name <文件路径> \
  --gemini_key <API密钥> \
  --api_base https://www.packyapi.com \
  --model packygemini \
  --model_list <模型名称> \
  --language zh-hans
```

### 测试模式

```bash
# 只翻译前 2 段进行测试
python make_book.py \
  --book_name test_books/test_simple.txt \
  --gemini_key sk-X13SEBiTbMjD2bLkkxTpxay6X2lLf4i58yK9xfRb7ZQ6AbXC \
  --api_base https://www.packyapi.com \
  --model packygemini \
  --model_list gemini-3-pro-preview \
  --test --test_num 2
```

### 完整翻译

```bash
# 翻译 EPUB 书籍
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --gemini_key sk-X13SEBiTbMjD2bLkkxTpxay6X2lLf4i58yK9xfRb7ZQ6AbXC \
  --api_base https://www.packyapi.com \
  --model packygemini \
  --model_list gemini-3-pro-preview \
  --language zh-hans
```

## 支持的模型

- `gemini-3-flash-preview`：速度快，成本低（默认）
- `gemini-3-pro-preview`：翻译质量更高

## 配置参数

| 参数 | 说明 | 必需 |
|------|------|------|
| `--gemini_key` | PackyAPI 的 API 密钥 | 是 |
| `--api_base` | API 基础 URL（默认：https://www.packyapi.com） | 是 |
| `--model` | 翻译器类型，使用 `packygemini` | 是 |
| `--model_list` | Gemini 模型名称 | 是 |
| `--language` | 目标语言（如 zh-hans, en, ja） | 是 |
| `--test` | 测试模式，只翻译部分内容 | 否 |
| `--test_num` | 测试模式下翻译的段落数 | 否 |

## 环境变量

可以通过环境变量设置 API 密钥：

```bash
export BBM_GOOGLE_GEMINI_KEY=sk-your-api-key-here
```

然后命令中可以省略 `--gemini_key` 参数。

## 输出文件

翻译完成后，双语文件会保存在与原文件相同的目录下：

- 文件名格式：`{原文件名}_bilingual.{扩展名}`
- 例如：
  - `test_books/animal_farm_bilingual.epub`
  - `test_books/test_simple_bilingual.txt`

## 自定义提示词

支持自定义翻译提示词：

```bash
python make_book.py \
  --book_name test_books/animal_farm.epub \
  --gemini_key <API密钥> \
  --api_base https://www.packyapi.com \
  --model packygemini \
  --model_list gemini-3-pro-preview \
  --prompt "请将以下文本翻译成{language}：{text}"
```

## 错误处理

翻译器内置了重试机制：
- 自动重试 3 次
- 使用指数退避策略
- 超时时间：60 秒

## 注意事项

1. **API 密钥兼容性**：确保你的 API 密钥支持 Gemini 原生 API 格式
2. **网络连接**：需要稳定的网络连接到 PackyAPI 服务器
3. **速率限制**：默认请求间隔为 3 秒，可通过代码调整
4. **中断恢复**：使用 `--resume` 参数可以在中断后继续翻译

## 故障排查

### 401 错误（未提供密钥）
- 检查 `--gemini_key` 参数是否正确
- 确认 API 密钥有效

### 403 错误（权限拒绝）
- 确认 API 密钥支持所选模型
- 尝试更换模型（如从 flash 换到 pro）

### 超时错误
- 检查网络连接
- 尝试增加超时时间
- 使用更快的模型（如 flash）

## 技术细节

### 请求格式示例

```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Translate this to Chinese: Hello world"
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 1.0
  }
}
```

### 响应格式示例

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "你好世界"
          }
        ]
      }
    }
  ]
}
```

## 更新日志

- **2026-01-13**：初始版本，支持 Gemini 原生 API 格式
