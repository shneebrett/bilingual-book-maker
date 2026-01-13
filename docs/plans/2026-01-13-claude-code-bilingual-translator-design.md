# Claude Code 双语翻译器设计方案

**创建日期：** 2026-01-13
**状态：** 设计中
**版本：** 0.1

## 项目背景

当前 bilingual_book_maker 项目使用外部 API（如 OpenAI、Claude API）进行翻译，但在使用中转站 API key 时存在适配问题：
- 中转站主要为 CLI 工具（claude code、codex、gemini）服务
- 缺乏规范的 HTTP API 文档
- 请求经常被拒绝

## 设计目标

创建一个基于 Claude Code 的翻译工作流，直接利用 Claude Code 的翻译能力，无需外部 API key。

## 核心需求

1. **交互方式**：混合模式（自动翻译 + 关键节点审核）
2. **翻译粒度**：灵活可配置（可在运行时选择处理多少段落）
3. **技术方案**：混合方案（创建 skill 处理交互逻辑 + 复用现有项目的文件处理代码）

---

## 第一部分：整体架构和组件 ✅

### 系统架构

这个方案由 **3 个核心组件** 组成：

#### 1. Claude Code Skill（`bilingual-translator`）
- **位置**：`~/.claude/skills/bilingual-translator/`
- **职责**：处理用户交互、翻译流程编排、审核逻辑
- **技术**：Markdown 格式的 skill 定义文件

#### 2. MCP 服务器（`bilingual-book-mcp`）
- **位置**：在现有项目中新增 `mcp_server/` 目录
- **职责**：暴露现有项目的 loader/writer 功能为 MCP 工具
- **技术**：Python + FastMCP
- **工具集**：
  - `load_book`: 加载 epub/txt/srt 文件
  - `get_content`: 获取指定范围的内容（章节/段落）
  - `save_translation`: 保存翻译结果到指定位置
  - `get_progress`: 获取翻译进度

#### 3. 现有项目模块（复用）
- `book_maker/loader/`: 文件加载逻辑
- `book_maker/utils.py`: 工具函数
- **不使用**现有的 translator 模块（翻译由 Claude Code 完成）

### 组件交互流程

```
用户 <-> Claude Code Skill <-> MCP Server <-> 现有项目模块
                                    ↓
                              文件系统（epub/txt）
```

### MCP Server 实现复杂度

**最小化实现**（约 30 行核心代码）：

```python
# mcp_server/server.py
from mcp.server.fastmcp import FastMCP
from book_maker.loader import BOOK_LOADER_DICT

mcp = FastMCP("bilingual-book-mcp")

@mcp.tool()
def load_book(file_path: str, book_type: str = "epub"):
    """加载书籍文件"""
    loader_class = BOOK_LOADER_DICT.get(book_type)
    loader = loader_class(file_path)
    return {"chapters": len(loader.chapters), "title": loader.title}

@mcp.tool()
def get_content(file_path: str, chapter_index: int, start: int = 0, count: int = 10):
    """获取指定章节的内容片段"""
    # 调用现有 loader 逻辑
    pass

@mcp.tool()
def save_translation(file_path: str, chapter_index: int, translations: list):
    """保存翻译结果"""
    # 调用现有 writer 逻辑
    pass
```

**配置文件**（`~/.claude/mcp_settings.json`）：

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

**依赖安装**：
```bash
pip install mcp
```

---

## 第二部分：数据流和交互流程 ✅

### 完整工作流程

**用户启动翻译：**
```bash
/bilingual-translator --book test_books/animal_farm.epub --language zh-hans --batch-size 10
```

**Skill 执行流程：**

#### 阶段 1：初始化（自动）
1. 调用 `load_book` 工具加载文件
2. 获取书籍元数据（章节数、标题等）
3. 询问用户确认翻译范围（全书 / 指定章节）

#### 阶段 2：翻译循环（混合自动+审核）
```
for each batch:
  1. 调用 get_content 获取 N 个段落
  2. Claude Code 翻译这些段落（使用自身能力）
  3. 展示翻译结果（原文 + 译文对照）
  4. 询问用户：
     - ✅ 接受并继续
     - ✏️ 修改后继续
     - ⏭️ 跳过这批
     - ⏸️ 暂停保存进度
  5. 如果接受，调用 save_translation 保存
  6. 每 N 批（可配置）自动暂停审核
```

#### 阶段 3：完成和输出
1. 所有批次完成后，调用 MCP 工具生成最终双语文件
2. 展示统计信息（总段落数、翻译时间、跳过的段落等）
3. 询问是否需要导出翻译记录（用于后续审核）

### 数据结构

**翻译批次对象：**
```json
{
  "batch_id": 1,
  "chapter_index": 0,
  "start_paragraph": 0,
  "paragraphs": [
    {
      "index": 0,
      "original": "It was a bright cold day in April...",
      "translation": "四月的一天，天气寒冷晴朗...",
      "status": "accepted"
    }
  ]
}
```

**进度状态：**
```json
{
  "book_path": "test_books/animal_farm.epub",
  "total_chapters": 10,
  "current_chapter": 2,
  "current_paragraph": 45,
  "completed_paragraphs": 45,
  "skipped_paragraphs": 2,
  "last_save_time": "2026-01-13T10:30:00"
}
```

---

## 第三部分：MCP 工具详细定义 ✅

### 核心 MCP 工具接口

#### 1. `load_book` - 加载书籍

**功能**：加载并解析书籍文件，返回元数据。

**参数：**
```python
file_path: str          # 书籍文件路径
book_type: str = "epub" # 文件类型：epub, txt, srt, md
```

**返回：**
```json
{
  "success": true,
  "book_id": "uuid-xxx",
  "title": "Animal Farm",
  "author": "George Orwell",
  "language": "en",
  "total_chapters": 10,
  "total_paragraphs": 1234,
  "chapters": [
    {"index": 0, "title": "Chapter I", "paragraph_count": 120}
  ]
}
```

#### 2. `get_content` - 获取内容片段

**功能**：获取指定范围的原文内容。

**参数：**
```python
book_id: str           # 书籍 ID
chapter_index: int     # 章节索引
start: int = 0         # 起始段落索引
count: int = 10        # 获取段落数量
```

**返回：**
```json
{
  "success": true,
  "chapter_index": 0,
  "chapter_title": "Chapter I",
  "paragraphs": [
    {
      "index": 0,
      "text": "It was a bright cold day in April...",
      "html": "<p>It was a bright cold day in April...</p>",
      "tag": "p"
    }
  ],
  "has_more": true
}
```

#### 3. `save_translation` - 保存翻译

**功能**：保存翻译结果到内存缓存。

**参数：**
```python
book_id: str
chapter_index: int
translations: list[dict]  # [{"index": 0, "original": "...", "translation": "..."}]
```

**返回：**
```json
{
  "success": true,
  "saved_count": 10,
  "progress_percentage": 8.5
}
```

#### 4. `export_bilingual_book` - 导出双语书籍

**功能**：生成最终的双语文件。

**参数：**
```python
book_id: str
output_path: str = None  # 默认为 {original}_bilingual.epub
```

**返回：**
```json
{
  "success": true,
  "output_path": "test_books/animal_farm_bilingual.epub",
  "file_size": "2.3 MB"
}
```

#### 5. `get_progress` - 获取进度

**功能**：获取当前翻译进度。

**参数：**
```python
book_id: str
```

**返回：**（与第二部分定义的进度状态一致）

---

## 第四部分：错误处理和恢复机制 ✅

### 错误类型和处理策略

#### 1. 文件加载错误
**场景**：文件不存在、格式损坏、权限不足

**处理**：
- 立即向用户报告错误信息
- 提供修复建议（检查路径、文件格式）
- 允许用户重新指定文件

#### 2. 翻译中断
**场景**：用户手动中断、网络问题、Claude Code 崩溃

**恢复机制**：
- 每保存一批翻译后，自动保存进度到 `.translation_state.json`
- 重启时检测到未完成的翻译，询问是否恢复
- 恢复时从上次保存的位置继续

**进度文件格式**：
```json
{
  "book_id": "uuid-xxx",
  "book_path": "test_books/animal_farm.epub",
  "language": "zh-hans",
  "batch_size": 10,
  "last_completed_chapter": 2,
  "last_completed_paragraph": 45,
  "timestamp": "2026-01-13T10:30:00"
}
```

#### 3. MCP 工具调用失败
**场景**：MCP 服务器未启动、工具返回错误

**处理**：
- 重试机制（最多 3 次，指数退避）
- 失败后提示用户检查 MCP 配置
- 提供手动重启 MCP 服务器的指令

#### 4. 翻译质量问题
**场景**：用户不满意翻译结果

**处理**：
- 提供"修改后继续"选项，允许用户编辑译文
- 提供"重新翻译"选项，使用不同的提示词
- 记录用户修改，用于改进后续翻译

### 数据持久化策略

**临时文件**：
- `.translation_state.json`：进度状态
- `.translation_cache/`：已翻译内容缓存（按章节分文件）

**清理机制**：
- 翻译完成后询问是否删除临时文件
- 保留选项：用于后续审核或重新导出

---

## 第五部分：配置选项和使用方式 ✅

### Skill 调用方式

**基本用法：**
```bash
/bilingual-translator --book test_books/animal_farm.epub --language zh-hans
```

**完整参数：**
```bash
/bilingual-translator \
  --book <file_path>              # 必需：书籍文件路径
  --language <target_lang>        # 必需：目标语言（zh-hans, ja, fr 等）
  --batch-size <number>           # 可选：每批处理段落数（默认 10）
  --review-interval <number>      # 可选：每 N 批暂停审核（默认 5）
  --resume                        # 可选：恢复上次中断的翻译
  --output <file_path>            # 可选：输出文件路径
  --chapters <range>              # 可选：指定章节范围（如 1-3,5）
```

### 配置文件

**位置**：`~/.claude/skills/bilingual-translator/config.json`

**内容：**
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

### 使用示例

**场景 1：首次翻译**
```bash
/bilingual-translator --book animal_farm.epub --language zh-hans --batch-size 15
```

**场景 2：恢复中断的翻译**
```bash
/bilingual-translator --resume
```

**场景 3：只翻译特定章节**
```bash
/bilingual-translator --book book.epub --language ja --chapters 1-3,7
```

### 翻译提示词自定义

用户可以在配置文件中自定义翻译提示词，支持变量：
- `{text}`：原文内容
- `{language}`：目标语言
- `{chapter_title}`：当前章节标题

---

## 第六部分：实现计划 ✅

### 实现阶段划分

#### 阶段 1：MCP 服务器开发（核心基础）

**任务：**
1. 创建 `mcp_server/` 目录结构
2. 实现 5 个核心 MCP 工具
3. 编写单元测试
4. 配置 MCP 服务器到 Claude Code

**预期产出：**
- `mcp_server/server.py`：MCP 服务器主文件
- `mcp_server/book_manager.py`：书籍管理逻辑
- `mcp_server/tests/`：测试文件
- `~/.claude/mcp_settings.json`：配置文件

**验收标准：**
- 所有 5 个工具可以正常调用
- 能够加载 epub 文件并返回正确的元数据
- 能够保存和导出双语文件

---

#### 阶段 2：Claude Code Skill 开发（交互层）

**任务：**
1. 创建 skill 目录和定义文件
2. 实现参数解析和验证
3. 实现翻译循环逻辑
4. 实现审核交互流程

**预期产出：**
- `~/.claude/skills/bilingual-translator/skill.md`：Skill 定义
- `~/.claude/skills/bilingual-translator/config.json`：配置文件

**验收标准：**
- 可以通过 `/bilingual-translator` 调用
- 参数解析正确
- 能够展示翻译结果并接收用户反馈

---

#### 阶段 3：错误处理和恢复机制（健壮性）

**任务：**
1. 实现进度保存和恢复
2. 实现重试机制
3. 实现错误提示和修复建议
4. 添加临时文件管理

**预期产出：**
- 进度文件自动保存
- `--resume` 参数可用
- 错误提示清晰

**验收标准：**
- 中断后可以恢复
- MCP 工具失败会自动重试
- 用户能够理解错误信息

---

#### 阶段 4：测试和优化（质量保证）

**任务：**
1. 端到端测试（使用 `animal_farm.epub`）
2. 性能优化（批量处理、缓存）
3. 用户体验优化（提示信息、进度显示）
4. 文档完善

**预期产出：**
- 测试报告
- 性能基准
- 用户手册

**验收标准：**
- 能够成功翻译完整书籍
- 翻译质量满足要求
- 用户体验流畅

---

### 技术栈

- **MCP 服务器**：Python 3.8+, FastMCP
- **Skill**：Markdown, JSON
- **现有项目依赖**：ebooklib, beautifulsoup4

### 关键风险和缓解措施

**风险 1：MCP 服务器稳定性**
- 缓解：充分测试，添加日志，实现重启机制

**风险 2：翻译质量不稳定**
- 缓解：提供自定义提示词，允许用户修改译文

**风险 3：大文件处理性能**
- 缓解：分批处理，增量保存，优化内存使用

---

## 总结

本设计方案提供了一个基于 Claude Code 的双语翻译工作流，核心优势：

1. **无需外部 API key**：直接使用 Claude Code 的翻译能力
2. **灵活可控**：混合自动化和人工审核
3. **复用现有代码**：最大化利用 bilingual_book_maker 项目
4. **易于扩展**：MCP 架构便于添加新功能

**下一步行动：**
- 使用 `/superpowers:writing-plans` 创建详细实现计划
- 开始阶段 1 的实现

---

**状态：** 设计完成 ✅
**最后更新：** 2026-01-13
