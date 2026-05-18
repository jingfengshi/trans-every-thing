"""
E2E test fixtures.

Strategy:
- FastAPI via TestClient (real routes)
- Celery task_always_eager=True (sync, no Redis needed)
- Translator mocked (no real API calls)
- PDF processing real (PyMuPDF)
"""
import io
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# ---------- mock translator factory ----------

def make_mock_translator(translations: dict[str, str] | None = None):
    """
    Returns a mock BaseTranslator.
    translations: {source_text: translated_text}
    If not provided, prepends '[ZH]' (or target lang tag) to each text.
    """
    class MockTranslator:
        def translate(self, texts: list[str], target_lang: str, style_prompt: str = "") -> list[str]:
            result = []
            for t in texts:
                if translations and t in translations:
                    result.append(translations[t])
                else:
                    tag = f"[{target_lang.upper()}]"
                    result.append(f"{tag} {t}")
            return result
    return MockTranslator()


# ---------- app client with Celery eager mode ----------

@pytest.fixture
def app_client(tmp_path):
    """
    TestClient with:
    - Celery tasks run synchronously (task_always_eager)
    - Translator mocked
    - Upload/output dirs in tmp_path
    """
    upload_dir = tmp_path / "uploads"
    output_dir = tmp_path / "outputs"
    upload_dir.mkdir()
    output_dir.mkdir()

    mock_translator = make_mock_translator()

    with (
        patch("tasks.UPLOAD_DIR", upload_dir),
        patch("tasks.OUTPUT_DIR", output_dir),
        patch("main.UPLOAD_DIR", upload_dir),
        patch("main.OUTPUT_DIR", output_dir),
        patch("translator.factory.get_translator", return_value=mock_translator),
        patch("tasks.get_translator", return_value=mock_translator),
    ):
        from main import app
        from tasks import celery_app
        celery_app.conf.update(
            task_always_eager=True,
            task_eager_propagates=True,
            task_store_eager_result=True,
        )

        with TestClient(app) as client:
            yield client, output_dir

        # reset eager mode
        celery_app.conf.update(task_always_eager=False)


@pytest.fixture
def app_client_with_translations(tmp_path):
    """Same as app_client but accepts custom translation map."""
    def _factory(translations: dict[str, str]):
        upload_dir = tmp_path / "uploads"
        output_dir = tmp_path / "outputs"
        upload_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)

        mock_translator = make_mock_translator(translations)

        ctx = (
            patch("tasks.UPLOAD_DIR", upload_dir),
            patch("tasks.OUTPUT_DIR", output_dir),
            patch("main.UPLOAD_DIR", upload_dir),
            patch("main.OUTPUT_DIR", output_dir),
            patch("translator.factory.get_translator", return_value=mock_translator),
            patch("tasks.get_translator", return_value=mock_translator),
        )
        return ctx, output_dir

    return _factory


# ---------- helpers ----------

def pdf_bytes(path: str | Path) -> bytes:
    return Path(path).read_bytes()


def extract_text_from_pdf(path: str | Path) -> str:
    import fitz
    doc = fitz.open(str(path))
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def submit_and_wait(client, pdf_path: str | Path, engine="claude", target_lang="zh", style_prompt=""):
    """Upload PDF and return (response_json, task_id)."""
    data = {"engine": engine, "target_lang": target_lang}
    if style_prompt:
        data["style_prompt"] = style_prompt

    resp = client.post(
        "/api/translate",
        data=data,
        files={"file": (Path(pdf_path).name, pdf_bytes(pdf_path), "application/pdf")},
    )
    assert resp.status_code == 200, f"Upload failed: {resp.text}"
    return resp.json()
