import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def make_pdf_bytes():
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "Hello World", fontsize=14)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture
def client():
    from main import app
    return TestClient(app)


@patch("main.translate_file")
def test_submit_translate(mock_task, client):
    mock_task.apply_async.return_value = MagicMock(id="test-uuid")

    pdf_bytes = make_pdf_bytes()
    response = client.post(
        "/api/translate",
        data={"engine": "claude", "target_lang": "zh"},
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"


@patch("main.translate_file")
def test_submit_translate_with_style(mock_task, client):
    mock_task.apply_async.return_value = MagicMock(id="test-uuid")

    pdf_bytes = make_pdf_bytes()
    response = client.post(
        "/api/translate",
        data={"engine": "claude", "target_lang": "zh", "style_prompt": "翻译成粤语"},
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    call_args = mock_task.apply_async.call_args
    assert "翻译成粤语" in call_args[1]["args"]


def test_submit_invalid_engine(client):
    pdf_bytes = make_pdf_bytes()
    response = client.post(
        "/api/translate",
        data={"engine": "invalid", "target_lang": "zh"},
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 400


@patch("main.AsyncResult")
def test_get_status_pending(mock_result, client):
    mock_result.return_value.state = "PENDING"
    response = client.get("/api/status/some-task-id")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"


@patch("main.AsyncResult")
def test_get_status_processing(mock_result, client):
    mock_result.return_value.state = "PROGRESS"
    mock_result.return_value.info = {"progress": 0.5}
    response = client.get("/api/status/some-task-id")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    assert data["progress"] == 0.5


@patch("main.AsyncResult")
def test_get_status_done(mock_result, client):
    mock_result.return_value.state = "SUCCESS"
    response = client.get("/api/status/some-task-id")
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_download_not_found(client):
    response = client.get("/api/download/nonexistent-id")
    assert response.status_code == 404
