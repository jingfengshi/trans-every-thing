import os
from google.cloud import translate_v2 as google_translate
from .base import BaseTranslator


class GoogleTranslator(BaseTranslator):
    def __init__(self, api_key: str | None = None):
        key = api_key or os.environ.get("GOOGLE_TRANSLATE_API_KEY", "")
        self.client = google_translate.Client(client_options={"api_key": key})

    def translate(self, texts: list[str], target_lang: str, style_prompt: str = "") -> list[str]:
        # Google Translate 不支持风格提示词，忽略 style_prompt
        if not texts:
            return []
        results = self.client.translate(texts, target_language=target_lang)
        return [r["translatedText"] for r in results]
