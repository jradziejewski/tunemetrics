"""
TuneMetrics – /analyze Route
------------------------------
Accepts an uploaded audio file, runs the audio processing pipeline,
and returns extracted music features as JSON.

Flow
----
  1. Validate file type (extension check)
  2. Save file to a temporary location
  3. Run librosa analysis
  4. Delete the temporary file  ← always, even on error
  5. Return structured JSON
"""

import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models import AnalysisResponse, ChromagramResult, KeyDetectionResult
from app.services.audio_processor import process_audio
from app.utils.file_utils import delete_file, save_upload_temporarily, validate_audio_file

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze an audio file",
    description=(
        "Upload a `.mp3` or `.wav` file. "
        "The API returns tempo (BPM), a chromagram, and a key-detection placeholder."
    ),
    responses={
        400: {"description": "Unsupported file type or missing filename"},
        413: {"description": "File exceeds the size limit"},
        422: {"description": "Audio could not be decoded"},
        500: {"description": "Internal processing error"},
    },
)
async def analyze_audio(
    file: UploadFile = File(..., description="Audio file (.mp3 or .wav)"),
) -> AnalysisResponse:
    # ── 1. Validate ───────────────────────────────────────────────────────────
    validate_audio_file(file)

    # ── 2. Save temporarily ───────────────────────────────────────────────────
    tmp_path: Path = await save_upload_temporarily(file)

    # ── 3 & 4. Process then clean up (finally = always runs) ─────────────────
    try:
        logger.info("Analysing '%s'", file.filename)
        features = process_audio(tmp_path)
    except HTTPException:
        raise  # Let FastAPI handle known HTTP errors
    except Exception as exc:
        logger.exception("Unexpected error while processing '%s'", file.filename)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.") from exc
    finally:
        delete_file(tmp_path)

    # ── 5. Build and return response ──────────────────────────────────────────
    return AnalysisResponse(
        filename=file.filename,
        duration_seconds=features["duration_seconds"],
        tempo_bpm=features["tempo_bpm"],
        chromagram=ChromagramResult(**features["chromagram"]),
        key_detection=KeyDetectionResult(**features["key_detection"]),
    )
