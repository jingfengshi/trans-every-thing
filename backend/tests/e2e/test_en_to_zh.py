"""E2E: 英文 PDF → 中文翻译"""
import fitz
import pytest
from pathlib import Path
from .conftest import FIXTURES_DIR, submit_and_wait, extract_text_from_pdf


def test_en_to_zh_full_pipeline(app_client):
    client, output_dir = app_client
    pdf_path = FIXTURES_DIR / "en_simple.pdf"

    result = submit_and_wait(client, pdf_path, engine="claude", target_lang="zh")

    assert "task_id" in result
    task_id = result["task_id"]

    # 状态应为 done（eager mode 同步完成）
    status = client.get(f"/api/status/{task_id}").json()
    assert status["status"] == "done", f"Task status: {status}"

    # 输出文件存在
    output_path = output_dir / f"{task_id}_translated.pdf"
    assert output_path.exists(), "Output PDF not created"

    # 输出 PDF 可读，页数一致
    original = fitz.open(str(pdf_path))
    output = fitz.open(str(output_path))
    assert output.page_count == original.page_count
    original.close()
    output.close()


def test_en_to_zh_text_present(app_client):
    """输出 PDF 包含译文标记（mock 译文格式：[ZH] original）"""
    client, output_dir = app_client
    pdf_path = FIXTURES_DIR / "en_simple.pdf"

    result = submit_and_wait(client, pdf_path, target_lang="zh")
    output_path = output_dir / f"{result['task_id']}_translated.pdf"

    text = extract_text_from_pdf(output_path)
    # mock translator prepends [ZH] — 验证译文写入成功，不是空白/点号
    assert "[ZH]" in text, f"Translation marker not found in output. Got: {text[:300]}"


def test_en_to_zh_download_endpoint(app_client):
    client, output_dir = app_client
    pdf_path = FIXTURES_DIR / "en_simple.pdf"

    result = submit_and_wait(client, pdf_path, target_lang="zh")
    task_id = result["task_id"]

    resp = client.get(f"/api/download/{task_id}")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 100  # 非空 PDF


def test_en_to_zh_font_sizes_preserved(app_client):
    """输出 PDF 中字体大小应与原文接近（±3pt）"""
    client, output_dir = app_client
    pdf_path = FIXTURES_DIR / "en_simple.pdf"

    # 读原始字体大小
    original_doc = fitz.open(str(pdf_path))
    orig_sizes = set()
    for page in original_doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:
                for line in block["lines"]:
                    for span in line["spans"]:
                        orig_sizes.add(round(span["size"]))
    original_doc.close()

    result = submit_and_wait(client, pdf_path, target_lang="zh")
    output_path = output_dir / f"{result['task_id']}_translated.pdf"

    output_doc = fitz.open(str(output_path))
    out_sizes = set()
    for page in output_doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:
                for line in block["lines"]:
                    for span in line["spans"]:
                        out_sizes.add(round(span["size"]))
    output_doc.close()

    # 至少一个字体大小与原文匹配（容差 3pt）
    matched = any(
        any(abs(o - r) <= 3 for r in out_sizes)
        for o in orig_sizes
    )
    assert matched, f"No font size match. Original: {orig_sizes}, Output: {out_sizes}"
