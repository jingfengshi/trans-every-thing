from pathlib import Path
from .base import BaseProcessor
from .pdf import PDFProcessor
from .excel import ExcelProcessor

_PROCESSORS: dict[str, type[BaseProcessor]] = {
    ".pdf": PDFProcessor,
    ".xlsx": ExcelProcessor,
    ".xls": ExcelProcessor,
}


def get_processor(file_path: str) -> BaseProcessor:
    ext = Path(file_path).suffix.lower()
    if ext not in _PROCESSORS:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {list(_PROCESSORS.keys())}")
    return _PROCESSORS[ext]()
