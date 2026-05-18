from .base import BaseProcessor, TextBlock


class ExcelProcessor(BaseProcessor):
    def extract_blocks(self, file_path: str) -> list[TextBlock]:
        raise NotImplementedError("Excel support not yet implemented")

    def rebuild(self, original_path: str, blocks: list[TextBlock], output_path: str) -> None:
        raise NotImplementedError("Excel support not yet implemented")
