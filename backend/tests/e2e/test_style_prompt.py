"""E2E: 风格提示词影响翻译结果"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from .conftest import FIXTURES_DIR, submit_and_wait, extract_text_from_pdf, make_mock_translator


def test_style_prompt_passed_to_translator(tmp_path):
    """验证 style_prompt 确实传递到翻译引擎"""
    upload_dir = tmp_path / "uploads"
    output_dir = tmp_path / "outputs"
    upload_dir.mkdir()
    output_dir.mkdir()

    received_styles = []

    class StyleCapturingTranslator:
        def translate(self, texts, target_lang, style_prompt=""):
            received_styles.append(style_prompt)
            return [f"[{target_lang.upper()}] {t}" for t in texts]

    capturing = StyleCapturingTranslator()

    with (
        patch("tasks.UPLOAD_DIR", upload_dir),
        patch("tasks.OUTPUT_DIR", output_dir),
        patch("main.UPLOAD_DIR", upload_dir),
        patch("main.OUTPUT_DIR", output_dir),
        patch("translator.factory.get_translator", return_value=capturing),
        patch("tasks.get_translator", return_value=capturing),
    ):
        from main import app
        from tasks import celery_app
        from fastapi.testclient import TestClient

        celery_app.conf.update(
            task_always_eager=True,
            task_eager_propagates=True,
            task_store_eager_result=True,
        )

        with TestClient(app) as client:
            submit_and_wait(
                client,
                FIXTURES_DIR / "en_simple.pdf",
                target_lang="zh",
                style_prompt="使用口语化表达",
            )

        celery_app.conf.update(task_always_eager=False)

    assert any("口语化" in s for s in received_styles), \
        f"Style prompt not passed to translator. Received: {received_styles}"


def test_no_style_prompt_default_behavior(app_client):
    """不填风格提示词时正常完成"""
    client, output_dir = app_client
    result = submit_and_wait(
        client,
        FIXTURES_DIR / "en_simple.pdf",
        target_lang="zh",
        style_prompt="",
    )
    assert client.get(f"/api/status/{result['task_id']}").json()["status"] == "done"


def test_style_prompt_does_not_break_output(app_client):
    """填写风格提示词后输出 PDF 依然可读"""
    client, output_dir = app_client
    result = submit_and_wait(
        client,
        FIXTURES_DIR / "en_simple.pdf",
        target_lang="zh",
        style_prompt="翻译成粤语，保留专业术语",
    )
    output_path = output_dir / f"{result['task_id']}_translated.pdf"
    assert output_path.exists()
    text = extract_text_from_pdf(output_path)
    assert len(text.strip()) > 0
