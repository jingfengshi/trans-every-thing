import pytest
import fitz
from processors.base import TextBlock, BaseProcessor


def make_test_pdf(path: str):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 100), "Hello World", fontsize=14)
    page.insert_text((50, 150), "This is a test.", fontsize=12)
    doc.save(path)
    doc.close()

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

    for block in blocks:
        block.text = "你好世界" if "Hello" in block.text else "这是测试。"

    processor.rebuild(pdf_path, blocks, output_path)

    doc = fitz.open(output_path)
    assert doc.page_count == 1
    doc.close()


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
