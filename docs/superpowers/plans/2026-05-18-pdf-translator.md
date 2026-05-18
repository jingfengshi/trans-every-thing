# PDF 翻译工具实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建 Web 应用，用户上传 PDF，选择翻译引擎、目标语言和可选风格提示词，下载保持原版面的翻译 PDF。

**Architecture:** FastAPI 后端 + Celery 异步任务队列，PyMuPDF 处理 PDF 文本块提取与重建，翻译引擎通过统一抽象接口支持 Claude/OpenAI/Google 三种引擎。Vue.js 前端轮询任务状态，Docker Compose 一键启动。

**Tech Stack:** Python 3.11, FastAPI, Celery, Redis, PyMuPDF (fitz), Vue 3, Vite, Docker Compose

---

## Task 1: 项目骨架与 Docker 配置

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/Dockerfile`

- [ ] **Step 1: 创建 .env.example**

```bash
cat > .env.example << 'EOF'
CLAUDE_API_KEY=
OPENAI_API_KEY=
GOOGLE_TRANSLATE_API_KEY=
REDIS_URL=redis://redis:6379/0
MAX_FILE_SIZE_MB=50
EOF
```

- [ ] **Step 2: 创建 backend/requirements.txt**

```
fastapi==0.111.0
uvicorn[standard]==0.30.1
celery==5.4.0
redis==5.0.6
pymupdf==1.24.5
anthropic==0.28.0
openai==1.35.3
google-cloud-translate==3.15.3
python-multipart==0.0.9
aiofiles==23.2.1
pytest==8.2.2
httpx==0.27.0
pytest-asyncio==0.23.7
```

- [ ] **Step 3: 创建 backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 4: 创建 frontend/package.json**

```json
{
  "name": "trans-every-thing-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "axios": "^1.7.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.3.0"
  }
}
```

- [ ] **Step 5: 创建 frontend/vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      }
    }
  }
})
```

- [ ] **Step 6: 创建 frontend/Dockerfile**

```dockerfile
FROM node:20-slim

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

CMD ["npm", "run", "dev"]
```

- [ ] **Step 7: 创建 docker-compose.yml**

```yaml
version: '3.9'

services:
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./backend:/app
      - ./tmp:/tmp/trans
    depends_on:
      - redis

  worker:
    build: ./backend
    command: celery -A tasks worker --loglevel=info --concurrency=2
    env_file: .env
    volumes:
      - ./backend:/app
      - ./tmp:/tmp/trans
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

- [ ] **Step 8: 复制 .env**

```bash
cp .env.example .env
```

- [ ] **Step 9: Commit**

```bash
git init
git add .
git commit -m "chore: project scaffold and docker config"
```

---

## Task 2: 文本块数据结构与 BaseProcessor

**Files:**
- Create: `backend/processors/__init__.py`
- Create: `backend/processors/base.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_processors.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/tests/test_processors.py`：

```python
import pytest
from processors.base import TextBlock, BaseProcessor

def test_text_block_creation():
    block = TextBlock(
        text="Hello",
        x=10.0, y=20.0,
        width=100.0, height=20.0,
        font_size=12.0,
        font_name="Helvetica",
        page=0,
        metadata={}
    )
    assert block.text == "Hello"
    assert block.page == 0

def test_base_processor_is_abstract():
    with pytest.raises(TypeError):
        BaseProcessor()
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd backend && python -m pytest tests/test_processors.py -v
```

Expected: `ModuleNotFoundError: No module named 'processors'`

- [ ] **Step 3: 实现 processors/base.py**

```python
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

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
    metadata: dict = field(default_factory=dict)

class BaseProcessor(ABC):
    @abstractmethod
    def extract_blocks(self, file_path: str) -> list[TextBlock]:
        """从文件提取所有文本块"""

    @abstractmethod
    def rebuild(self, original_path: str, blocks: list[TextBlock], output_path: str) -> None:
        """将翻译后的文本块写回文件"""
```

创建 `backend/processors/__init__.py`（空文件）和 `backend/tests/__init__.py`（空文件）。

- [ ] **Step 4: 运行测试，确认通过**

```bash
cd backend && python -m pytest tests/test_processors.py -v
```

Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/processors/ backend/tests/
git commit -m "feat: TextBlock dataclass and BaseProcessor abstract class"
```

---

## Task 3: PDFProcessor 实现

**Files:**
- Create: `backend/processors/pdf.py`
- Modify: `backend/tests/test_processors.py`

需要一个真实的小 PDF 用于测试。测试中用 PyMuPDF 动态生成。

- [ ] **Step 1: 补充 PDF 测试**

在 `backend/tests/test_processors.py` 末尾追加：

```python
import fitz  # PyMuPDF

def make_test_pdf(path: str):
    """创建包含文字的测试 PDF"""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 100), "Hello World", fontsize=14)
    page.insert_text((50, 150), "This is a test.", fontsize=12)
    doc.save(path)
    doc.close()

def test_pdf_processor_extract_blocks(tmp_path):
    from processors.pdf import PDFProcessor
    pdf_path = str(tmp_path / "test.pdf")
    make_test_pdf(pdf_path)

    processor = PDFProcessor()
    blocks = processor.extract_blocks(pdf_path)

    assert len(blocks) > 0
    assert any("Hello World" in b.text for b in blocks)
    assert all(b.page == 0 for b in blocks)
    assert all(b.x >= 0 and b.y >= 0 for b in blocks)

def test_pdf_processor_rebuild(tmp_path):
    from processors.pdf import PDFProcessor
    pdf_path = str(tmp_path / "test.pdf")
    output_path = str(tmp_path / "output.pdf")
    make_test_pdf(pdf_path)

    processor = PDFProcessor()
    blocks = processor.extract_blocks(pdf_path)

    # 模拟翻译：将文本替换
    for block in blocks:
        block.text = "你好世界" if "Hello" in block.text else "这是测试。"

    processor.rebuild(pdf_path, blocks, output_path)

    # 验证输出文件存在且可读
    doc = fitz.open(output_path)
    assert doc.page_count == 1
    doc.close()
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd backend && python -m pytest tests/test_processors.py::test_pdf_processor_extract_blocks -v
```

Expected: `ImportError: cannot import name 'PDFProcessor'`

- [ ] **Step 3: 实现 processors/pdf.py**

```python
import fitz  # PyMuPDF
from pathlib import Path
from .base import BaseProcessor, TextBlock

FALLBACK_FONT = "cjk"  # PyMuPDF 内置 CJK 字体

class PDFProcessor(BaseProcessor):
    def extract_blocks(self, file_path: str) -> list[TextBlock]:
        blocks = []
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc):
            for block in page.get_text("dict")["blocks"]:
                if block["type"] != 0:  # 0 = text, 1 = image
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue
                        bbox = span["bbox"]  # (x0, y0, x1, y1)
                        blocks.append(TextBlock(
                            text=text,
                            x=bbox[0],
                            y=bbox[1],
                            width=bbox[2] - bbox[0],
                            height=bbox[3] - bbox[1],
                            font_size=span["size"],
                            font_name=span["font"],
                            page=page_num,
                            metadata={
                                "color": span["color"],
                                "flags": span["flags"],
                                "origin": span["origin"],
                            }
                        ))
        doc.close()
        return blocks

    def rebuild(self, original_path: str, blocks: list[TextBlock], output_path: str) -> None:
        doc = fitz.open(original_path)

        # 按页分组
        pages_blocks: dict[int, list[TextBlock]] = {}
        for block in blocks:
            pages_blocks.setdefault(block.page, []).append(block)

        for page_num, page_blocks in pages_blocks.items():
            page = doc[page_num]
            for block in page_blocks:
                rect = fitz.Rect(block.x, block.y, block.x + block.width, block.y + block.height)
                # 用白色矩形覆盖原文字
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                # 写入译文，回退到 CJK 字体
                try:
                    page.insert_text(
                        (block.x, block.y + block.height * 0.8),
                        block.text,
                        fontsize=block.font_size,
                        color=self._int_to_rgb(block.metadata.get("color", 0)),
                    )
                except Exception:
                    page.insert_text(
                        (block.x, block.y + block.height * 0.8),
                        block.text,
                        fontname=FALLBACK_FONT,
                        fontsize=block.font_size,
                        color=self._int_to_rgb(block.metadata.get("color", 0)),
                    )

        doc.save(output_path)
        doc.close()

    @staticmethod
    def _int_to_rgb(color_int: int) -> tuple[float, float, float]:
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return (r, g, b)
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
cd backend && python -m pytest tests/test_processors.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/processors/pdf.py backend/tests/test_processors.py
git commit -m "feat: PDFProcessor with PyMuPDF extract and rebuild"
```

---

## Task 4: 翻译引擎抽象 + 三种实现

**Files:**
- Create: `backend/translator/__init__.py`
- Create: `backend/translator/base.py`
- Create: `backend/translator/claude.py`
- Create: `backend/translator/openai.py`
- Create: `backend/translator/google.py`
- Create: `backend/translator/factory.py`
- Create: `backend/tests/test_translators.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/tests/test_translators.py`：

```python
import pytest
from unittest.mock import patch, MagicMock
from translator.factory import get_translator
from translator.base import BaseTranslator

def test_get_translator_claude():
    t = get_translator("claude")
    assert isinstance(t, BaseTranslator)

def test_get_translator_openai():
    t = get_translator("openai")
    assert isinstance(t, BaseTranslator)

def test_get_translator_google():
    t = get_translator("google")
    assert isinstance(t, BaseTranslator)

def test_get_translator_invalid():
    with pytest.raises(ValueError, match="Unsupported engine"):
        get_translator("unknown")

@patch("anthropic.Anthropic")
def test_claude_translate(mock_anthropic):
    from translator.claude import ClaudeTranslator

    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_client.messages.create.return_value.content = [
        MagicMock(text="你好\n世界")
    ]

    t = ClaudeTranslator(api_key="test-key")
    result = t.translate(["Hello", "World"], target_lang="zh")
    assert result == ["你好", "世界"]

@patch("anthropic.Anthropic")
def test_claude_translate_with_style(mock_anthropic):
    from translator.claude import ClaudeTranslator

    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_client.messages.create.return_value.content = [
        MagicMock(text="1. 你好\n2. 世界")
    ]

    t = ClaudeTranslator(api_key="test-key")
    t.translate(["Hello", "World"], target_lang="zh", style_prompt="翻译成粤语")

    call_args = mock_client.messages.create.call_args
    prompt_content = call_args[1]["messages"][0]["content"]
    assert "粤语" in prompt_content

@patch("openai.OpenAI")
def test_openai_translate(mock_openai):
    from translator.openai import OpenAITranslator

    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="你好\n世界"))
    ]

    t = OpenAITranslator(api_key="test-key")
    result = t.translate(["Hello", "World"], target_lang="zh")
    assert result == ["你好", "世界"]
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd backend && python -m pytest tests/test_translators.py -v
```

Expected: `ModuleNotFoundError: No module named 'translator'`

- [ ] **Step 3: 实现 translator/base.py**

```python
from abc import ABC, abstractmethod

class BaseTranslator(ABC):
    @abstractmethod
    def translate(self, texts: list[str], target_lang: str, style_prompt: str = "") -> list[str]:
        """批量翻译文本列表，返回等长译文列表。style_prompt 非空时注入翻译风格。"""
```

- [ ] **Step 4: 实现 translator/claude.py**

```python
import os
import anthropic
from .base import BaseTranslator

LANG_NAMES = {"zh": "Chinese", "en": "English", "ja": "Japanese", "ko": "Korean", "fr": "French", "de": "German", "es": "Spanish"}

class ClaudeTranslator(BaseTranslator):
    def __init__(self, api_key: str | None = None):
        self.client = anthropic.Anthropic(api_key=api_key or os.environ["CLAUDE_API_KEY"])

    def translate(self, texts: list[str], target_lang: str, style_prompt: str = "") -> list[str]:
        lang_name = LANG_NAMES.get(target_lang, target_lang)
        numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
        style_instruction = f" Additional style requirement: {style_prompt}" if style_prompt.strip() else ""
        prompt = (
            f"Translate the following numbered texts to {lang_name}.{style_instruction} "
            f"Return ONLY the translations, one per line, same numbering. "
            f"Do not add explanations.\n\n{numbered}"
        )
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        lines = response.content[0].text.strip().split("\n")
        results = []
        for line in lines:
            # 去除 "1. " 前缀
            if ". " in line:
                results.append(line.split(". ", 1)[1])
            else:
                results.append(line)
        # 确保与输入等长
        while len(results) < len(texts):
            results.append(texts[len(results)])
        return results[:len(texts)]
```

- [ ] **Step 5: 实现 translator/openai.py**

```python
import os
import openai as openai_lib
from .base import BaseTranslator

LANG_NAMES = {"zh": "Chinese", "en": "English", "ja": "Japanese", "ko": "Korean", "fr": "French", "de": "German", "es": "Spanish"}

class OpenAITranslator(BaseTranslator):
    def __init__(self, api_key: str | None = None):
        self.client = openai_lib.OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])

    def translate(self, texts: list[str], target_lang: str, style_prompt: str = "") -> list[str]:
        lang_name = LANG_NAMES.get(target_lang, target_lang)
        numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
        style_instruction = f" Additional style requirement: {style_prompt}" if style_prompt.strip() else ""
        prompt = (
            f"Translate the following numbered texts to {lang_name}.{style_instruction} "
            f"Return ONLY the translations, one per line, same numbering. "
            f"Do not add explanations.\n\n{numbered}"
        )
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        lines = response.choices[0].message.content.strip().split("\n")
        results = []
        for line in lines:
            if ". " in line:
                results.append(line.split(". ", 1)[1])
            else:
                results.append(line)
        while len(results) < len(texts):
            results.append(texts[len(results)])
        return results[:len(texts)]
```

- [ ] **Step 6: 实现 translator/google.py**

```python
import os
from google.cloud import translate_v2 as google_translate
from .base import BaseTranslator

class GoogleTranslator(BaseTranslator):
    def __init__(self, api_key: str | None = None):
        key = api_key or os.environ.get("GOOGLE_TRANSLATE_API_KEY", "")
        self.client = google_translate.Client(client_options={"api_key": key})

    def translate(self, texts: list[str], target_lang: str, style_prompt: str = "") -> list[str]:
        # Google Translate 不支持风格提示词，忽略 style_prompt
        if not texts:
            return []
        results = self.client.translate(texts, target_language=target_lang)
        return [r["translatedText"] for r in results]
```

- [ ] **Step 7: 实现 translator/factory.py**

```python
from .base import BaseTranslator
from .claude import ClaudeTranslator
from .openai import OpenAITranslator
from .google import GoogleTranslator

_ENGINES: dict[str, type[BaseTranslator]] = {
    "claude": ClaudeTranslator,
    "openai": OpenAITranslator,
    "google": GoogleTranslator,
}

def get_translator(engine: str) -> BaseTranslator:
    if engine not in _ENGINES:
        raise ValueError(f"Unsupported engine: {engine}. Choose from {list(_ENGINES.keys())}")
    return _ENGINES[engine]()
```

创建 `backend/translator/__init__.py`（空文件）。

- [ ] **Step 8: 运行测试，确认通过**

```bash
cd backend && python -m pytest tests/test_translators.py -v
```

Expected: `5 passed`

- [ ] **Step 9: Commit**

```bash
git add backend/translator/ backend/tests/test_translators.py
git commit -m "feat: translator abstraction with Claude, OpenAI, Google implementations"
```

---

## Task 5: Processor 工厂 + 占位实现

**Files:**
- Create: `backend/processors/factory.py`
- Create: `backend/processors/excel.py`
- Create: `backend/processors/word.py`

- [ ] **Step 1: 写失败测试**

在 `backend/tests/test_processors.py` 末尾追加：

```python
def test_get_processor_pdf(tmp_path):
    from processors.factory import get_processor
    pdf_path = str(tmp_path / "test.pdf")
    make_test_pdf(pdf_path)
    processor = get_processor(pdf_path)
    from processors.pdf import PDFProcessor
    assert isinstance(processor, PDFProcessor)

def test_get_processor_unsupported():
    from processors.factory import get_processor
    with pytest.raises(ValueError, match="Unsupported file type"):
        get_processor("/tmp/test.txt")
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd backend && python -m pytest tests/test_processors.py::test_get_processor_pdf -v
```

Expected: `ImportError: cannot import name 'get_processor'`

- [ ] **Step 3: 实现 processors/factory.py**

```python
from pathlib import Path
from .base import BaseProcessor
from .pdf import PDFProcessor

_PROCESSORS: dict[str, type[BaseProcessor]] = {
    ".pdf": PDFProcessor,
}

def get_processor(file_path: str) -> BaseProcessor:
    ext = Path(file_path).suffix.lower()
    if ext not in _PROCESSORS:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {list(_PROCESSORS.keys())}")
    return _PROCESSORS[ext]()
```

- [ ] **Step 4: 创建占位文件**

`backend/processors/excel.py`：
```python
# TODO: implement when openpyxl support is added
from .base import BaseProcessor, TextBlock

class ExcelProcessor(BaseProcessor):
    def extract_blocks(self, file_path: str) -> list[TextBlock]:
        raise NotImplementedError("Excel support not yet implemented")

    def rebuild(self, original_path: str, blocks: list[TextBlock], output_path: str) -> None:
        raise NotImplementedError("Excel support not yet implemented")
```

`backend/processors/word.py`：
```python
# TODO: implement when python-docx support is added
from .base import BaseProcessor, TextBlock

class WordProcessor(BaseProcessor):
    def extract_blocks(self, file_path: str) -> list[TextBlock]:
        raise NotImplementedError("Word support not yet implemented")

    def rebuild(self, original_path: str, blocks: list[TextBlock], output_path: str) -> None:
        raise NotImplementedError("Word support not yet implemented")
```

- [ ] **Step 5: 运行测试，确认通过**

```bash
cd backend && python -m pytest tests/test_processors.py -v
```

Expected: `6 passed`

- [ ] **Step 6: Commit**

```bash
git add backend/processors/
git commit -m "feat: processor factory and placeholder Excel/Word processors"
```

---

## Task 6: Celery 任务 + FastAPI 后端

**Files:**
- Create: `backend/tasks.py`
- Create: `backend/main.py`
- Create: `backend/tests/test_api.py`

- [ ] **Step 1: 实现 tasks.py**

```python
import os
import uuid
from pathlib import Path
from celery import Celery
from processors.factory import get_processor
from translator.factory import get_translator

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
UPLOAD_DIR = Path("/tmp/trans/uploads")
OUTPUT_DIR = Path("/tmp/trans/outputs")

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.update(task_track_started=True)

@celery_app.task(bind=True)
def translate_file(self, task_id: str, file_path: str, engine: str, target_lang: str, style_prompt: str = ""):
    try:
        self.update_state(state="PROGRESS", meta={"progress": 0.1})

        processor = get_processor(file_path)
        blocks = processor.extract_blocks(file_path)

        self.update_state(state="PROGRESS", meta={"progress": 0.3})

        translator = get_translator(engine)
        texts = [b.text for b in blocks]

        # 分批翻译，每批 50 个
        batch_size = 50
        translated_texts = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            translated_texts.extend(translator.translate(batch, target_lang, style_prompt))
            progress = 0.3 + 0.6 * (i + batch_size) / max(len(texts), 1)
            self.update_state(state="PROGRESS", meta={"progress": min(progress, 0.9)})

        for block, translated in zip(blocks, translated_texts):
            block.text = translated

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = str(OUTPUT_DIR / f"{task_id}_translated.pdf")
        processor.rebuild(file_path, blocks, output_path)

        self.update_state(state="SUCCESS", meta={"progress": 1.0, "output_path": output_path})
        return {"output_path": output_path}

    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
```

- [ ] **Step 2: 实现 main.py**

```python
import os
import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult
from tasks import celery_app, translate_file, UPLOAD_DIR, OUTPUT_DIR

app = FastAPI(title="Trans Every Thing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_ENGINES = {"claude", "openai", "google"}
MAX_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", 50))

@app.post("/api/translate")
async def submit_translate(
    file: UploadFile = File(...),
    engine: str = Form(...),
    target_lang: str = Form(...),
    style_prompt: str = Form(default=""),
):
    if engine not in SUPPORTED_ENGINES:
        raise HTTPException(400, f"engine must be one of {SUPPORTED_ENGINES}")

    content = await file.read()
    if len(content) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"File too large. Max {MAX_SIZE_MB}MB.")

    task_id = str(uuid.uuid4())
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = str(UPLOAD_DIR / f"{task_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(content)

    translate_file.apply_async(
        args=[task_id, file_path, engine, target_lang, style_prompt],
        task_id=task_id,
    )

    return {"task_id": task_id, "status": "pending"}

@app.get("/api/status/{task_id}")
def get_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    state = result.state

    if state == "PENDING":
        return {"task_id": task_id, "status": "pending", "progress": 0.0, "error": None}
    elif state == "PROGRESS":
        meta = result.info or {}
        return {"task_id": task_id, "status": "processing", "progress": meta.get("progress", 0.0), "error": None}
    elif state == "SUCCESS":
        return {"task_id": task_id, "status": "done", "progress": 1.0, "error": None}
    elif state == "FAILURE":
        return {"task_id": task_id, "status": "failed", "progress": 0.0, "error": str(result.info)}
    else:
        return {"task_id": task_id, "status": state.lower(), "progress": 0.0, "error": None}

@app.get("/api/download/{task_id}")
def download_result(task_id: str):
    output_path = OUTPUT_DIR / f"{task_id}_translated.pdf"
    if not output_path.exists():
        raise HTTPException(404, "Result not ready or not found")
    return FileResponse(
        str(output_path),
        media_type="application/pdf",
        filename=f"{task_id}_translated.pdf",
    )
```

- [ ] **Step 3: 写 API 测试**

创建 `backend/tests/test_api.py`：

```python
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import io

@pytest.fixture
def client():
    from main import app
    return TestClient(app)

def make_pdf_bytes():
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "Hello World", fontsize=14)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

@patch("main.translate_file")
def test_submit_translate(mock_task, client):
    mock_task.apply_async.return_value = MagicMock(id="test-uuid")

    pdf_bytes = make_pdf_bytes()
    response = client.post(
        "/api/translate",
        data={"engine": "claude", "target_lang": "zh"},
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"

def test_submit_invalid_engine(client):
    pdf_bytes = make_pdf_bytes()
    response = client.post(
        "/api/translate",
        data={"engine": "invalid", "target_lang": "zh"},
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 400

@patch("main.AsyncResult")
def test_get_status_pending(mock_result, client):
    mock_result.return_value.state = "PENDING"
    response = client.get("/api/status/some-task-id")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"

def test_download_not_found(client):
    response = client.get("/api/download/nonexistent-id")
    assert response.status_code == 404
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
cd backend && python -m pytest tests/test_api.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/tasks.py backend/main.py backend/tests/test_api.py
git commit -m "feat: FastAPI routes and Celery translation task"
```

---

## Task 7: Vue.js 前端

**Files:**
- Create: `frontend/src/api.js`
- Create: `frontend/src/components/UploadPanel.vue`
- Create: `frontend/src/components/ProgressBar.vue`
- Create: `frontend/src/components/DownloadPanel.vue`
- Create: `frontend/src/App.vue`
- Create: `frontend/index.html`

- [ ] **Step 1: 创建 frontend/index.html**

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Trans Every Thing</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 2: 创建 frontend/src/main.js**

```javascript
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
```

- [ ] **Step 3: 创建 frontend/src/api.js**

```javascript
import axios from 'axios'

const BASE = '/api'

export async function submitTranslate(file, engine, targetLang, stylePrompt = '') {
  const form = new FormData()
  form.append('file', file)
  form.append('engine', engine)
  form.append('target_lang', targetLang)
  if (stylePrompt.trim()) form.append('style_prompt', stylePrompt.trim())
  const res = await axios.post(`${BASE}/translate`, form)
  return res.data // { task_id, status }
}

export async function getStatus(taskId) {
  const res = await axios.get(`${BASE}/status/${taskId}`)
  return res.data // { task_id, status, progress, error }
}

export function getDownloadUrl(taskId) {
  return `${BASE}/download/${taskId}`
}
```

- [ ] **Step 4: 创建 UploadPanel.vue**

```vue
<template>
  <div class="upload-panel">
    <div
      class="drop-zone"
      :class="{ dragover }"
      @dragover.prevent="dragover = true"
      @dragleave="dragover = false"
      @drop.prevent="onDrop"
      @click="$refs.fileInput.click()"
    >
      <span v-if="!file">拖拽 PDF 到此处，或点击选择文件</span>
      <span v-else>已选择：{{ file.name }}</span>
      <input ref="fileInput" type="file" accept=".pdf" hidden @change="onFileChange" />
    </div>

    <div class="options">
      <label>
        翻译引擎：
        <select v-model="engine">
          <option value="claude">Claude</option>
          <option value="openai">OpenAI</option>
          <option value="google">Google</option>
        </select>
      </label>

      <label>
        目标语言：
        <select v-model="targetLang">
          <option value="zh">中文</option>
          <option value="en">English</option>
          <option value="ja">日本語</option>
          <option value="ko">한국어</option>
          <option value="fr">Français</option>
          <option value="de">Deutsch</option>
          <option value="es">Español</option>
        </select>
      </label>
    </div>

    <label class="style-label">
      翻译风格（可选）：
      <textarea
        v-model="stylePrompt"
        placeholder="例如：翻译成粤语、保留专业术语、使用口语化表达..."
        rows="3"
      />
    </label>

    <button :disabled="!file || loading" @click="submit">
      {{ loading ? '提交中...' : '开始翻译' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { submitTranslate } from '../api.js'

const emit = defineEmits(['submitted'])

const file = ref(null)
const engine = ref('claude')
const targetLang = ref('zh')
const stylePrompt = ref('')
const dragover = ref(false)
const loading = ref(false)

function onFileChange(e) {
  file.value = e.target.files[0] || null
}

function onDrop(e) {
  dragover.value = false
  file.value = e.dataTransfer.files[0] || null
}

async function submit() {
  if (!file.value) return
  loading.value = true
  try {
    const data = await submitTranslate(file.value, engine.value, targetLang.value, stylePrompt.value)
    emit('submitted', data.task_id)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.upload-panel { display: flex; flex-direction: column; gap: 16px; }
.drop-zone {
  border: 2px dashed #aaa; border-radius: 8px; padding: 40px;
  text-align: center; cursor: pointer; transition: border-color 0.2s;
}
.drop-zone.dragover { border-color: #4f8ef7; background: #f0f5ff; }
.options { display: flex; gap: 24px; }
.style-label { display: flex; flex-direction: column; gap: 6px; }
.style-label textarea { resize: vertical; padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px; }
button { padding: 10px 24px; font-size: 16px; cursor: pointer; }
button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
```

- [ ] **Step 5: 创建 ProgressBar.vue**

```vue
<template>
  <div class="progress-wrap">
    <p>{{ statusText }}</p>
    <div class="bar-bg">
      <div class="bar-fill" :style="{ width: `${progress * 100}%` }" />
    </div>
    <p v-if="error" class="error">错误：{{ error }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: String,
  progress: Number,
  error: String,
})

const statusText = computed(() => ({
  pending: '等待处理...',
  processing: `翻译中 ${Math.round(props.progress * 100)}%`,
  done: '翻译完成！',
  failed: '翻译失败',
}[props.status] || props.status))
</script>

<style scoped>
.bar-bg { background: #eee; border-radius: 4px; height: 8px; overflow: hidden; }
.bar-fill { background: #4f8ef7; height: 100%; transition: width 0.3s; }
.error { color: red; }
</style>
```

- [ ] **Step 6: 创建 DownloadPanel.vue**

```vue
<template>
  <div class="download-panel">
    <p>翻译完成，点击下载：</p>
    <a :href="downloadUrl" download>
      <button>下载翻译 PDF</button>
    </a>
    <button class="secondary" @click="$emit('reset')">翻译新文件</button>
  </div>
</template>

<script setup>
import { getDownloadUrl } from '../api.js'

const props = defineProps({ taskId: String })
defineEmits(['reset'])

const downloadUrl = getDownloadUrl(props.taskId)
</script>

<style scoped>
.download-panel { display: flex; flex-direction: column; gap: 12px; align-items: flex-start; }
button { padding: 10px 24px; font-size: 16px; cursor: pointer; }
.secondary { background: #eee; }
</style>
```

- [ ] **Step 7: 创建 App.vue**

```vue
<template>
  <div class="app">
    <h1>Trans Every Thing</h1>

    <UploadPanel v-if="stage === 'upload'" @submitted="onSubmitted" />

    <ProgressBar
      v-if="stage === 'progress'"
      :status="taskStatus.status"
      :progress="taskStatus.progress"
      :error="taskStatus.error"
    />

    <DownloadPanel
      v-if="stage === 'done'"
      :task-id="taskId"
      @reset="reset"
    />
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import UploadPanel from './components/UploadPanel.vue'
import ProgressBar from './components/ProgressBar.vue'
import DownloadPanel from './components/DownloadPanel.vue'
import { getStatus } from './api.js'

const stage = ref('upload')
const taskId = ref(null)
const taskStatus = ref({ status: 'pending', progress: 0, error: null })
let pollTimer = null

async function onSubmitted(id) {
  taskId.value = id
  stage.value = 'progress'
  startPolling()
}

function startPolling() {
  pollTimer = setInterval(async () => {
    const data = await getStatus(taskId.value)
    taskStatus.value = data
    if (data.status === 'done') {
      clearInterval(pollTimer)
      stage.value = 'done'
    } else if (data.status === 'failed') {
      clearInterval(pollTimer)
    }
  }, 2000)
}

function reset() {
  stage.value = 'upload'
  taskId.value = null
  taskStatus.value = { status: 'pending', progress: 0, error: null }
}

onUnmounted(() => clearInterval(pollTimer))
</script>

<style>
body { font-family: sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; }
h1 { margin-bottom: 32px; }
</style>
```

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat: Vue.js frontend with upload, progress polling, download"
```

---

## Task 8: 运行全套测试 + 验收

- [ ] **Step 1: 运行所有后端测试**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: 所有测试通过

- [ ] **Step 2: 构建并启动 Docker Compose**

```bash
# 确保 .env 填入至少一个 API key
docker compose up --build
```

Expected:
- `frontend` 启动在 http://localhost:5173
- `backend` 启动在 http://localhost:8000
- `worker` 连接 Redis 成功
- `redis` 启动正常

- [ ] **Step 3: 手动验收**

1. 打开 http://localhost:5173
2. 拖拽一个英文 PDF 上传
3. 选择翻译引擎（需要有效 API Key）和目标语言"中文"
4. 点击"开始翻译"，观察进度条
5. 翻译完成后，点击下载
6. 打开下载的 PDF，确认文字已翻译，版面与原 PDF 一致

- [ ] **Step 4: Final Commit**

```bash
git add .
git commit -m "chore: final integration and docker-compose verified"
```
