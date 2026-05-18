from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class TextBlock:
    text: str
    x: float
    y: float
    width: float
    height: float
    font_size: float
    font_name: str
    page: int
    metadata: dict = field(default_factory=dict)


class BaseProcessor(ABC):
    @abstractmethod
    def extract_blocks(self, file_path: str) -> list[TextBlock]:
        """从文件提取所有文本块"""

    @abstractmethod
    def rebuild(self, original_path: str, blocks: list[TextBlock], output_path: str) -> None:
        """将翻译后的文本块写回文件"""
