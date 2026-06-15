"""
TuneMetrics – File Utilities
------------------------------
Helpers for validating and temporarily storing uploaded audio files.
"""

import uuid
import logging
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


def validate_audio_file(file: UploadFile) -> None:
    """
    Raise HTTP 400 if the uploaded file doesn't look like a supported audio file.

    Checks:
      1. The file extension is in ALLOWED_EXTENSIONS (.mp3 / .wav).
      2. A filename is actually present (not empty).
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in settings.ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(settings.ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Accepted types: {allowed}.",
        )


async def save_upload_temporarily(file: UploadFile) -> Path:
    """
    Stream the uploaded file to a temporary path inside UPLOAD_DIR.

    Returns the Path so the caller can pass it to librosa (and delete it later).

    A UUID prefix keeps concurrent uploads from colliding even if they share
    the same original filename.
    """
    suffix = Path(file.filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    dest = settings.UPLOAD_DIR / unique_name

    try:
        content = await file.read()

        # Basic size guard (reads whole file into memory – fine for ≤50 MB)
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum allowed size is {settings.MAX_FILE_SIZE_MB} MB.",
            )

        dest.write_bytes(content)
        logger.info("Saved upload to %s (%d bytes)", dest, len(content))
        return dest

    except HTTPException:
        raise  # re-raise size/validation errors as-is
    except Exception as exc:
        logger.exception("Failed to save uploaded file")
        raise HTTPException(status_code=500, detail="Could not save the uploaded file.") from exc


def delete_file(path: Path) -> None:
    """Remove a temporary file, logging a warning if it's already gone."""
    try:
        path.unlink(missing_ok=True)
        logger.debug("Deleted temporary file %s", path)
    except Exception:
        logger.warning("Could not delete temporary file %s", path, exc_info=True)
