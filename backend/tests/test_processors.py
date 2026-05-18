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
