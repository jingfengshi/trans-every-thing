from .base import BaseProcessor, TextBlock


class WordProcessor(BaseProcessor):
    def extract_blocks(self, file_path: str) -> list[TextBlock]:
        raise NotImplementedError("Word support not yet implemented")

    def rebuild(self, original_path: str, blocks: list[TextBlock], output_path: str) -> None:
        raise NotImplementedError("Word support not yet implemented")
