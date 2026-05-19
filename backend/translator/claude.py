import os
import anthropic
from .base import BaseTranslator

LANG_NAMES = {
    "zh": "Chinese", "en": "English", "ja": "Japanese",
    "ko": "Korean", "fr": "French", "de": "German", "es": "Spanish",
}


class ClaudeTranslator(BaseTranslator):
    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("CLAUDE_API_KEY", "")
        base_url = os.environ.get("ANTHROPIC_BASE_URL")
        kwargs = {"auth_token": self._api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = anthropic.Anthropic(**kwargs)

    def translate(self, texts: list[str], target_lang: str, style_prompt: str = "") -> list[str]:
        lang_name = LANG_NAMES.get(target_lang, target_lang)
        numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
        style_instruction = f" Additional style requirement: {style_prompt}" if style_prompt.strip() else ""
        prompt = (
            f"Translate the following numbered texts to {lang_name}.{style_instruction} "
            f"Return ONLY the translations, one per line, same numbering. "
            f"Do not add explanations.\n\n{numbered}"
        )
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        lines = response.content[0].text.strip().split("\n")
        results = []
        for line in lines:
            if ". " in line:
                results.append(line.split(". ", 1)[1])
            else:
                results.append(line)
        while len(results) < len(texts):
            results.append(texts[len(results)])
        return results[:len(texts)]
