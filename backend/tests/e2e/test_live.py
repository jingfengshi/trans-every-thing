"""
E2E live tests — 调用真实 API，需要有效的 CLAUDE_API_KEY。

运行：
    pytest tests/e2e/test_live.py -m live -v

CI 默认跳过（无 API key 时自动 skip）。
"""
import os
import fitz
import pytest
from pathlib import Path
from .conftest import FIXTURES_DIR, extract_text_from_pdf

pytestmark = pytest.mark.live

# 没有 key 则跳过整个模块
if not os.environ.get("CLAUDE_API_KEY"):
    pytest.skip("CLAUDE_API_KEY not set", allow_module_level=True)


@pytest.fixture
def live_client(tmp_path):
    from unittest.mock import patch
    from fastapi.testclient import TestClient

    upload_dir = tmp_path / "uploads"
    output_dir = tmp_path / "outputs"
    upload_dir.mkdir()
    output_dir.mkdir()

    with (
        patch("tasks.UPLOAD_DIR", upload_dir),
        patch("tasks.OUTPUT_DIR", output_dir),
        patch("main.UPLOAD_DIR", upload_dir),
        patch("main.OUTPUT_DIR", output_dir),
    ):
        from main import app
        from tasks import celery_app
        celery_app.conf.update(
            task_always_eager=True,
            task_eager_propagates=True,
            task_store_eager_result=True,
        )

        with TestClient(app) as client:
            yield client, output_dir

        celery_app.conf.update(task_always_eager=False)


def _submit(client, pdf_path, target_lang="zh", style_prompt=""):
    data = {"engine": "claude", "target_lang": target_lang}
    if style_prompt:
        data["style_prompt"] = style_prompt
    resp = client.post(
        "/api/translate",
        data=data,
        files={"file": (Path(pdf_path).name, Path(pdf_path).read_bytes(), "application/pdf")},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_live_en_to_zh(live_client):
    """真实翻译：英文 → 中文，验证输出含中文字符"""
    client, output_dir = live_client
    result = _submit(client, FIXTURES_DIR / "en_simple.pdf", target_lang="zh")
    task_id = result["task_id"]

    status = client.get(f"/api/status/{task_id}").json()
    assert status["status"] == "done", f"Failed: {status}"

    output_path = output_dir / f"{task_id}_translated.pdf"
    text = extract_text_from_pdf(output_path)

    # 验证包含中文字符
    has_chinese = any('一' <= c <= '鿿' for c in text)
    assert has_chinese, f"No Chinese characters in output. Got: {text[:300]}"


def test_live_en_to_ja(live_client):
    """真实翻译：英文 → 日文"""
    client, output_dir = live_client
    result = _submit(client, FIXTURES_DIR / "en_simple.pdf", target_lang="ja")

    status = client.get(f"/api/status/{result['task_id']}").json()
    assert status["status"] == "done"

    output_path = output_dir / f"{result['task_id']}_translated.pdf"
    text = extract_text_from_pdf(output_path)

    has_japanese = any('぀' <= c <= 'ヿ' for c in text)
    assert has_japanese, f"No Japanese characters in output. Got: {text[:300]}"


def test_live_style_cantonese(live_client):
    """真实翻译：英文 → 粤语风格"""
    client, output_dir = live_client
    result = _submit(
        client,
        FIXTURES_DIR / "en_simple.pdf",
        target_lang="zh",
        style_prompt="请翻译成粤语口语",
    )
    assert client.get(f"/api/status/{result['task_id']}").json()["status"] == "done"


def test_live_mixed_layout(live_client):
    """真实翻译：混排多字体文档"""
    client, output_dir = live_client
    result = _submit(client, FIXTURES_DIR / "mixed.pdf", target_lang="zh")

    status = client.get(f"/api/status/{result['task_id']}").json()
    assert status["status"] == "done"

    output_path = output_dir / f"{result['task_id']}_translated.pdf"
    orig = fitz.open(str(FIXTURES_DIR / "mixed.pdf"))
    out = fitz.open(str(output_path))
    assert out.page_count == orig.page_count
    orig.close()
    out.close()
