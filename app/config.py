"""
TuneMetrics – Application Configuration
----------------------------------------
All tuneable settings live here. Adjust via environment variables
or by editing the defaults below.
"""

from pathlib import Path


class Settings:
    # ── Project identity ──────────────────────────────────────────────────────
    APP_NAME: str = "TuneMetrics"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "Upload an audio file and get back music features like "
        "tempo (BPM), chromagram, and key detection."
    )

    # ── File upload ───────────────────────────────────────────────────────────
    UPLOAD_DIR: Path = Path("tmp_uploads")      # Temporary storage for uploads
    ALLOWED_EXTENSIONS: set[str] = {".mp3", ".wav"}
    MAX_FILE_SIZE_MB: int = 50                  # Reject files larger than this

    # ── Audio processing ──────────────────────────────────────────────────────
    SAMPLE_RATE: int = 22_050                   # librosa default sample rate
    HOP_LENGTH: int = 512                       # Frames between STFT windows
    N_CHROMA: int = 12                          # Chroma bins (one per pitch class)


# Single shared instance – import this everywhere
settings = Settings()

# Make sure the upload directory exists at startup
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
