import pytest
from unittest.mock import patch, MagicMock
from translator.factory import get_translator
from translator.base import BaseTranslator


@patch("translator.claude.anthropic.Anthropic")
def test_get_translator_claude(mock_anthropic):
    t = get_translator("claude")
    assert isinstance(t, BaseTranslator)


@patch("openai.OpenAI")
def test_get_translator_openai(mock_openai):
    t = get_translator("openai")
    assert isinstance(t, BaseTranslator)


@patch("google.cloud.translate_v2.Client")
def test_get_translator_google(mock_client):
    t = get_translator("google")
    assert isinstance(t, BaseTranslator)


def test_get_translator_invalid():
    with pytest.raises(ValueError, match="Unsupported engine"):
        get_translator("unknown")


@patch("anthropic.Anthropic")
def test_claude_translate(mock_anthropic):
    from translator.claude import ClaudeTranslator

    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_client.messages.create.return_value.content = [
        MagicMock(text="你好\n世界")
    ]

    t = ClaudeTranslator(api_key="test-key")
    result = t.translate(["Hello", "World"], target_lang="zh")
    assert result == ["你好", "世界"]


@patch("anthropic.Anthropic")
def test_claude_translate_with_style(mock_anthropic):
    from translator.claude import ClaudeTranslator

    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_client.messages.create.return_value.content = [
        MagicMock(text="1. 你好\n2. 世界")
    ]

    t = ClaudeTranslator(api_key="test-key")
    t.translate(["Hello", "World"], target_lang="zh", style_prompt="翻译成粤语")

    call_args = mock_client.messages.create.call_args
    prompt_content = call_args[1]["messages"][0]["content"]
    assert "粤语" in prompt_content


@patch("openai.OpenAI")
def test_openai_translate(mock_openai):
    from translator.openai import OpenAITranslator

    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="你好\n世界"))
    ]

    t = OpenAITranslator(api_key="test-key")
    result = t.translate(["Hello", "World"], target_lang="zh")
    assert result == ["你好", "世界"]
