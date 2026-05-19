# Trans Every Thing

> 文档智能翻译工具 — 支持 PDF / Excel，保留原始排版，多引擎驱动，左右对比预览。

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Vue](https://img.shields.io/badge/vue-3.x-green)

## 功能

- **PDF 翻译** — 保留原始字体、排版、图片位置，输出翻译后的 PDF
- **Excel 翻译** — 翻译所有文字单元格，保留样式、合并单元格、多 Sheet
- **多翻译引擎** — Claude / OpenAI / GPT / Google Translate 可切换
- **风格提示词** — 自定义翻译风格（粤语、专业术语、口语化等）
- **左右对比预览** — 翻译完成后原文/译文并排展示，同步滚动
- **异步任务队列** — Celery + Redis，大文件后台处理，进度实时展示

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite |
| 后端 | FastAPI + Celery |
| PDF 处理 | PyMuPDF |
| Excel 处理 | openpyxl |
| 队列/缓存 | Redis |
| 部署 | Docker Compose |

---

## 快速部署

### 前置要求

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 已安装并运行
- [Git](https://git-scm.com/) 已安装
- 至少一个翻译 API Key（Claude / OpenAI / Google）

### 1. 克隆项目

```bash
git clone https://github.com/jingfengshi/trans-every-thing.git
cd trans-every-thing
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

用编辑器打开 `.env`，填入 API Key：

```env
# 填入至少一个
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_TRANSLATE_API_KEY=...

# 如果使用 Claude 代理，填入代理地址
ANTHROPIC_BASE_URL=https://api.anthropic.com

# Redis（默认使用宿主机 Redis，见下方说明）
REDIS_URL=redis://host.docker.internal:6379/0

MAX_FILE_SIZE_MB=50
```

> **Redis 说明：** 项目默认连接宿主机的 Redis（`host.docker.internal:6379`）。  
> 如果宿主机没有 Redis，可以取消注释 `docker-compose.yml` 中的 redis 服务（见下方）。

### 3. 启动服务

```bash
docker compose up --build
```

首次启动需要拉取镜像并安装依赖，约需 3–5 分钟。

启动成功后看到：

```
worker-1  | celery@... ready.
backend-1 | Application startup complete.
frontend-1| VITE ... ready in ...ms
```

### 4. 打开浏览器

访问 [http://localhost:3000](http://localhost:3000)

---

## 使用说明

1. **上传文件** — 拖拽或点击选择 PDF / Excel（最大 50MB）
2. **选择引擎** — Claude / OpenAI / Google
3. **选择目标语言** — 中文 / 英文 / 日文等 7 种语言
4. **翻译风格**（可选）— 填写自定义提示词，如「翻译成粤语」
5. **开始翻译** — 等待进度条完成
6. **对比预览** — 左右分屏查看原文与译文
7. **下载** — 下载翻译后的文件

---

## 如果宿主机没有 Redis

在 `docker-compose.yml` 末尾添加 redis 服务，并修改 backend/worker 的依赖：

```yaml
services:
  # ... 现有服务 ...

  redis:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

同时将 backend 和 worker 的环境变量改为：

```yaml
environment:
  - REDIS_URL=redis://redis:6379/0
```

并加上依赖：

```yaml
depends_on:
  redis:
    condition: service_healthy
```

---

## 开发模式

后端和前端均支持热重载，修改代码后自动生效，无需重启容器。

```bash
# 只重建某个服务
docker compose up --build backend

# 查看日志
docker compose logs -f worker
docker compose logs -f backend
```

### 本地运行后端测试

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 运行所有测试（不调用真实 API）
pytest tests/ --ignore=tests/e2e/test_live.py -v

# 运行真实 API 测试（需要有效 Key）
CLAUDE_API_KEY=sk-... pytest tests/e2e/test_live.py -m live -v
```

---

## 项目结构

```
trans-every-thing/
├── backend/
│   ├── main.py              # FastAPI 路由
│   ├── tasks.py             # Celery 异步任务
│   ├── processors/
│   │   ├── pdf.py           # PDF 处理（PyMuPDF）
│   │   └── excel.py         # Excel 处理（openpyxl）
│   ├── translator/
│   │   ├── claude.py        # Claude 翻译引擎
│   │   ├── openai.py        # OpenAI 翻译引擎
│   │   └── google.py        # Google 翻译引擎
│   └── tests/               # 单元测试 + E2E 测试
├── frontend/
│   └── src/
│       ├── App.vue
│       └── components/
│           ├── UploadPanel.vue      # 上传表单
│           ├── ProgressBar.vue      # 进度展示
│           ├── DownloadPanel.vue    # 下载页
│           ├── CompareViewer.vue    # PDF 对比预览
│           └── ExcelCompareViewer.vue # Excel 对比预览
├── docker-compose.yml
└── .env.example
```

---

## API Key 获取

| 引擎 | 获取地址 |
|---|---|
| Claude | https://console.anthropic.com |
| OpenAI | https://platform.openai.com/api-keys |
| Google | https://console.cloud.google.com（启用 Cloud Translation API）|

---

## License

MIT
