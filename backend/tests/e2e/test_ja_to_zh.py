"""E2E: 日文 PDF → 中文翻译"""
import fitz
from .conftest import FIXTURES_DIR, submit_and_wait, extract_text_from_pdf


def test_ja_to_zh_pipeline(app_client):
    client, output_dir = app_client
    pdf_path = FIXTURES_DIR / "ja_source.pdf"

    result = submit_and_wait(client, pdf_path, engine="claude", target_lang="zh")
    task_id = result["task_id"]

    status = client.get(f"/api/status/{task_id}").json()
    assert status["status"] == "done", f"Task status: {status}"

    output_path = output_dir / f"{task_id}_translated.pdf"
    assert output_path.exists()


def test_ja_to_zh_text_present(app_client):
    client, output_dir = app_client
    pdf_path = FIXTURES_DIR / "ja_source.pdf"

    result = submit_and_wait(client, pdf_path, target_lang="zh")
    output_path = output_dir / f"{result['task_id']}_translated.pdf"

    text = extract_text_from_pdf(output_path)
    assert "[ZH]" in text, f"Translation marker not found. Got: {text[:300]}"


def test_ja_to_zh_output_readable(app_client):
    """输出 PDF 结构完整、可正常打开"""
    client, output_dir = app_client
    pdf_path = FIXTURES_DIR / "ja_source.pdf"

    result = submit_and_wait(client, pdf_path, target_lang="zh")
    output_path = output_dir / f"{result['task_id']}_translated.pdf"

    doc = fitz.open(str(output_path))
    assert doc.page_count >= 1
    assert not doc.is_encrypted
    doc.close()
