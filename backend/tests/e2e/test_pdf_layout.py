"""E2E: PDF 版面保留验证（混排文档）"""
import fitz
import pytest
from .conftest import FIXTURES_DIR, submit_and_wait, extract_text_from_pdf


def test_mixed_layout_pipeline(app_client):
    """多字体、多字号 PDF 能完整翻译"""
    client, output_dir = app_client
    result = submit_and_wait(client, FIXTURES_DIR / "mixed.pdf", target_lang="zh")
    assert client.get(f"/api/status/{result['task_id']}").json()["status"] == "done"


def test_mixed_layout_page_intact(app_client):
    client, output_dir = app_client
    result = submit_and_wait(client, FIXTURES_DIR / "mixed.pdf", target_lang="zh")
    output_path = output_dir / f"{result['task_id']}_translated.pdf"

    orig = fitz.open(str(FIXTURES_DIR / "mixed.pdf"))
    out  = fitz.open(str(output_path))
    assert out.page_count == orig.page_count
    orig_w = orig[0].rect.width
    out_w  = out[0].rect.width
    assert abs(orig_w - out_w) < 1, f"Page width changed: {orig_w} → {out_w}"
    orig.close()
    out.close()


def test_mixed_layout_multiple_font_sizes(app_client):
    """输出 PDF 应保留多种字号（原始有 28/16/14/11/10/8pt）"""
    client, output_dir = app_client
    result = submit_and_wait(client, FIXTURES_DIR / "mixed.pdf", target_lang="zh")
    output_path = output_dir / f"{result['task_id']}_translated.pdf"

    doc = fitz.open(str(output_path))
    sizes = set()
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:
                for line in block["lines"]:
                    for span in line["spans"]:
                        sizes.add(round(span["size"]))
    doc.close()

    assert len(sizes) >= 2, f"Expected multiple font sizes, got: {sizes}"


def test_all_engines_produce_output(app_client):
    """三种引擎都能跑通（mock 模式下）"""
    client, output_dir = app_client
    for engine in ["claude", "openai", "google"]:
        result = submit_and_wait(
            client, FIXTURES_DIR / "en_simple.pdf",
            engine=engine, target_lang="zh",
        )
        status = client.get(f"/api/status/{result['task_id']}").json()
        assert status["status"] == "done", f"Engine {engine} failed: {status}"


def test_all_target_languages(app_client):
    """所有目标语言都能正常完成"""
    client, output_dir = app_client
    for lang in ["zh", "en", "ja", "ko", "fr", "de", "es"]:
        result = submit_and_wait(
            client, FIXTURES_DIR / "en_simple.pdf",
            target_lang=lang,
        )
        status = client.get(f"/api/status/{result['task_id']}").json()
        assert status["status"] == "done", f"Lang {lang} failed: {status}"
        output_path = output_dir / f"{result['task_id']}_translated.pdf"
        assert output_path.exists(), f"Output missing for lang {lang}"
