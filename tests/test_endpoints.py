"""
TuneMetrics – Endpoint Tests
------------------------------
Run with:   pytest -v

These tests use FastAPI's TestClient (backed by httpx) so no real
server needs to be running.  Audio processing is mocked so the tests
stay fast and don't require actual audio files.
"""

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ── Fixtures ──────────────────────────────────────────────────────────────────

MOCK_FEATURES = {
    "duration_seconds": 42.0,
    "tempo_bpm": 120.0,
    "chromagram": {
        "pitch_classes": ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"],
        "mean_energy": [0.8, 0.1, 0.6, 0.2, 0.9, 0.3, 0.7, 0.4, 0.5, 0.3, 0.2, 0.6],
    },
    "key_detection": {
        "key": None,
        "confidence": None,
        "note": "Key detection is not yet implemented.",
    },
}


def _fake_mp3() -> BytesIO:
    """Return a tiny fake MP3 payload (not a real audio file – only for upload tests)."""
    return BytesIO(b"ID3" + b"\x00" * 128)


# ── Health ────────────────────────────────────────────────────────────────────

def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "TuneMetrics"


def test_health_includes_version():
    response = client.get("/health")
    assert "version" in response.json()


# ── /analyze – happy path ────────────────────────────────────────────────────

def test_analyze_valid_mp3(tmp_path):
    """A valid .mp3 upload with mocked processing should return 200."""
    with (
        patch("app.routes.analyze.save_upload_temporarily") as mock_save,
        patch("app.routes.analyze.process_audio", return_value=MOCK_FEATURES),
        patch("app.routes.analyze.delete_file"),
    ):
        mock_save.return_value = tmp_path / "fake.mp3"

        response = client.post(
            "/analyze",
            files={"file": ("song.mp3", _fake_mp3(), "audio/mpeg")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "song.mp3"
    assert body["tempo_bpm"] == 120.0
    assert len(body["chromagram"]["pitch_classes"]) == 12
    assert body["key_detection"]["key"] is None


def test_analyze_valid_wav(tmp_path):
    """A valid .wav upload should also succeed."""
    with (
        patch("app.routes.analyze.save_upload_temporarily") as mock_save,
        patch("app.routes.analyze.process_audio", return_value=MOCK_FEATURES),
        patch("app.routes.analyze.delete_file"),
    ):
        mock_save.return_value = tmp_path / "fake.wav"

        response = client.post(
            "/analyze",
            files={"file": ("beat.wav", BytesIO(b"RIFF" + b"\x00" * 44), "audio/wav")},
        )

    assert response.status_code == 200


# ── /analyze – error paths ────────────────────────────────────────────────────

def test_analyze_rejects_unsupported_type():
    """A .txt file should be rejected with 400."""
    response = client.post(
        "/analyze",
        files={"file": ("notes.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_analyze_rejects_pdf():
    """PDFs are not audio files."""
    response = client.post(
        "/analyze",
        files={"file": ("report.pdf", BytesIO(b"%PDF"), "application/pdf")},
    )
    assert response.status_code == 400


def test_analyze_propagates_processing_error(tmp_path):
    """If audio processing raises an HTTPException, it should bubble up."""
    from fastapi import HTTPException

    with (
        patch("app.routes.analyze.save_upload_temporarily") as mock_save,
        patch(
            "app.routes.analyze.process_audio",
            side_effect=HTTPException(status_code=422, detail="Bad audio"),
        ),
        patch("app.routes.analyze.delete_file"),
    ):
        mock_save.return_value = tmp_path / "bad.mp3"

        response = client.post(
            "/analyze",
            files={"file": ("bad.mp3", _fake_mp3(), "audio/mpeg")},
        )

    assert response.status_code == 422
