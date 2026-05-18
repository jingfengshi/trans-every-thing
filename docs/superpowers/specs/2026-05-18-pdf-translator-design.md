# PDF 翻译工具设计文档

**日期：** 2026-05-18  
**版本：** v1.1  
**范围：** PDF 翻译（保留原版面），预留多格式扩展点，支持自定义翻译风格提示词

---

## 1. 需求概述

用户上传 PDF，选择翻译引擎和目标语言，可选填写自定义风格提示词（如"翻译成粤语"、"保留专业术语"），系统翻译文字内容后输出保持原始版面的新 PDF。图片忽略，不做 OCR。

**当前支持格式：** PDF  
**预留扩展：** Excel、Word（架构已预留，暂不实现）

---

## 2. 整体架构

```
┌─────────────────────────────────────────┐
│  Vue.js 前端 (Vite)                      │
│  - 拖拽上传文件                          │
│  - 选择引擎 + 目标语言                   │
│  - 可选：自定义风格提示词文本框          │
│  - 进度轮询 + 下载结果                   │
└────────────────┬────────────────────────┘
                 │ HTTP REST
┌────────────────▼────────────────────────┐
│  FastAPI 后端                            │
│  POST /api/translate   提交任务          │
│  GET  /api/status/:id  查询进度          │
│  GET  /api/download/:id 下载结果文件     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  Celery Worker + Redis                   │
│  异步处理翻译任务，存储任务状态           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  文件处理核心                            │
│  Processor（按文件类型分发）             │
│    └── PDFProcessor (PyMuPDF)           │
│  Translator（按引擎分发）                │
│    ├── ClaudeTranslator                 │
│    ├── OpenAITranslator                 │
│    └── GoogleTranslator                 │
└─────────────────────────────────────────┘
```

---

## 3. 目录结构

```
trans-every-thing/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.vue
│       └── components/
│           ├── UploadPanel.vue      # 拖拽上传 + 引擎/语言选择
│           ├── ProgressBar.vue      # 轮询进度展示
│           └── DownloadPanel.vue    # 下载按钮
├── backend/
│   ├── main.py                      # FastAPI 路由
│   ├── tasks.py                     # Celery 任务定义
│   ├── processors/
│   │   ├── base.py                  # BaseProcessor 抽象类
│   │   ├── pdf.py                   # PDFProcessor (PyMuPDF)
│   │   ├── excel.py                 # 占位，未来实现
│   │   └── word.py                  # 占位，未来实现
│   ├── translator/
│   │   ├── base.py                  # BaseTranslator 抽象类
│   │   ├── claude.py                # Claude API
│   │   ├── openai.py                # OpenAI API
│   │   └── google.py                # Google Translate API
│   └── requirements.txt
├── docker-compose.yml
└── .env.example
```

---

## 4. 核心抽象接口

### 4.1 文件处理器

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class TextBlock:
    text: str
    x: float
    y: float
    width: float
    height: float
    font_size: float
    font_name: str
    page: int
    metadata: dict  # 各格式自定义字段

class BaseProcessor:
    def extract_blocks(self, file_path: str) -> list[TextBlock]: ...
    def rebuild(self, original_path: str, blocks: list[TextBlock], output_path: str) -> None: ...
```

新格式只需实现 `extract_blocks` 和 `rebuild`，翻译流程完全复用。

### 4.2 翻译引擎

```python
class BaseTranslator:
    def translate(self, texts: list[str], target_lang: str, style_prompt: str = "") -> list[str]: ...

class ClaudeTranslator(BaseTranslator): ...
class OpenAITranslator(BaseTranslator): ...
class GoogleTranslator(BaseTranslator): ...
```

批量翻译接口（`list[str]`）减少 API 调用次数。`style_prompt` 非空时追加到系统/用户 prompt 中，Google Translate 不支持提示词时忽略此参数。

### 4.3 工厂函数

```python
def get_processor(file_path: str) -> BaseProcessor:
    ext = Path(file_path).suffix.lower()
    return {".pdf": PDFProcessor, ".xlsx": ExcelProcessor, ".docx": WordProcessor}[ext]()

def get_translator(engine: str) -> BaseTranslator:
    return {"claude": ClaudeTranslator, "openai": OpenAITranslator, "google": GoogleTranslator}[engine]()
```

---

## 5. 数据流

```
1. 用户上传 PDF + 选择引擎/目标语言
   → POST /api/translate
   → 返回 task_id

2. FastAPI 保存原始文件到 /tmp/uploads/:task_id/
   → 推入 Celery 队列

3. Worker 执行：
   a. get_processor(file) → 解析文本块（含坐标、字体）
   b. get_translator(engine) → 批量翻译所有文本块
   c. processor.rebuild() → 译文写回原坐标 → 保存到 /tmp/outputs/:task_id/
   d. 更新 Redis 中任务状态为 done

4. 前端每 2 秒轮询 GET /api/status/:id
   → 状态 pending / processing / done / failed

5. done → 显示下载按钮
   → GET /api/download/:id → 返回结果文件
```

---

## 6. API 接口定义

### POST /api/translate
```json
// Request: multipart/form-data
{
  "file": "<binary>",
  "engine": "claude | openai | google",
  "target_lang": "zh | en | ja | ...",
  "style_prompt": "(可选) 翻译成粤语，保留专业术语"
}

// Response
{
  "task_id": "uuid",
  "status": "pending"
}
```

`style_prompt` 为空时，使用默认翻译行为。不为空时，注入到翻译引擎的系统提示词中。

### GET /api/status/:id
```json
{
  "task_id": "uuid",
  "status": "pending | processing | done | failed",
  "progress": 0.75,
  "error": null
}
```

### GET /api/download/:id
返回文件流，Content-Disposition 为原文件名加 `_translated` 后缀。

---

## 7. PDF 处理细节（PDFProcessor）

- 用 PyMuPDF (`fitz`) 逐页遍历文本块
- 每块保留：文字内容、bbox 坐标、字体名、字体大小、颜色
- 重建时：用白色矩形覆盖原文字区域，再在同位置写入译文
- 字体回退策略：优先用原字体，缺字则回退到 NotoSans（支持中文）
- 图片块跳过，直接保留

---

## 8. Docker 部署

```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports: ["5173:5173"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env
    volumes:
      - ./tmp:/tmp

  worker:
    build: ./backend
    command: celery -A tasks worker --loglevel=info
    env_file: .env
    volumes:
      - ./tmp:/tmp

  redis:
    image: redis:7-alpine
```

---

## 9. 环境变量（.env.example）

```
CLAUDE_API_KEY=
OPENAI_API_KEY=
GOOGLE_TRANSLATE_API_KEY=
REDIS_URL=redis://redis:6379/0
MAX_FILE_SIZE_MB=50
```

---

## 10. 扩展计划

| 格式 | 处理库 | 状态 |
|------|--------|------|
| PDF | PyMuPDF | ✅ 当前实现 |
| Excel | openpyxl | 🔲 预留 |
| Word | python-docx | 🔲 预留 |

添加新格式只需：实现 `BaseProcessor` + 在工厂函数注册后缀。
