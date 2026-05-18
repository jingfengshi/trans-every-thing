from .base import BaseTranslator
from .claude import ClaudeTranslator
from .openai import OpenAITranslator
from .google import GoogleTranslator

_ENGINES: dict[str, type[BaseTranslator]] = {
    "claude": ClaudeTranslator,
    "openai": OpenAITranslator,
    "google": GoogleTranslator,
}


def get_translator(engine: str) -> BaseTranslator:
    if engine not in _ENGINES:
        raise ValueError(f"Unsupported engine: {engine}. Choose from {list(_ENGINES.keys())}")
    return _ENGINES[engine]()
