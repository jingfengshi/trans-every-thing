import os
import uuid
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
