"""E2E: 中文 PDF → 英文翻译"""
import fitz
import pytest
from .conftest import FIXTURES_DIR, submit_and_wait, extract_text_from_pdf


def test_zh_to_en_pipeline(app_client):
    client, output_dir = app_client
    pdf_path = FIXTURES_DIR / "zh_source.pdf"

    result = submit_and_wait(client, pdf_path, engine="claude", target_lang="en")
    task_id = result["task_id"]

    status = client.get(f"/api/status/{task_id}").json()
    assert status["status"] == "done", f"Task status: {status}"

    output_path = output_dir / f"{task_id}_translated.pdf"
    assert output_path.exists()


def test_zh_to_en_text_present(app_client):
    client, output_dir = app_client
    pdf_path = FIXTURES_DIR / "zh_source.pdf"

    result = submit_and_wait(client, pdf_path, target_lang="en")
    output_path = output_dir / f"{result['task_id']}_translated.pdf"

    text = extract_text_from_pdf(output_path)
    assert "[EN]" in text, f"Translation marker not found. Got: {text[:300]}"


def test_zh_to_en_page_count_preserved(app_client):
    client, output_dir = app_client
    pdf_path = FIXTURES_DIR / "zh_source.pdf"

    result = submit_and_wait(client, pdf_path, target_lang="en")
    output_path = output_dir / f"{result['task_id']}_translated.pdf"

    orig = fitz.open(str(pdf_path))
    out = fitz.open(str(output_path))
    assert out.page_count == orig.page_count
    orig.close()
    out.close()
