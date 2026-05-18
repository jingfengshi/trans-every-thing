from abc import ABC, abstractmethod


class BaseTranslator(ABC):
    @abstractmethod
    def translate(self, texts: list[str], target_lang: str, style_prompt: str = "") -> list[str]:
        """批量翻译，返回等长译文列表。style_prompt 非空时注入翻译风格。"""
