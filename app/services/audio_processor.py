"""
TuneMetrics – Audio Processing Service
-----------------------------------------
All librosa calls are isolated here so that routes stay thin and
the processing logic is easy to test independently.

Public interface
----------------
  process_audio(file_path) -> dict   # called by the /analyze route
"""

import logging
from pathlib import Path

import librosa
import numpy as np
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

# The 12 standard pitch-class names used to label chroma bins
PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# ── Public entry point ────────────────────────────────────────────────────────

def process_audio(file_path: Path) -> dict:
    """
    Load an audio file and extract musical features.

    Parameters
    ----------
    file_path : Path
        Local path to a .mp3 or .wav file.

    Returns
    -------
    dict with keys:
        duration_seconds  float
        tempo_bpm         float
        chromagram        dict  (pitch_classes + mean_energy)
        key_detection     dict  (placeholder)
    """
    logger.info("Starting audio analysis for %s", file_path.name)

    y, sr = _load_audio(file_path)

    return {
        "duration_seconds": _get_duration(y, sr),
        "tempo_bpm": _extract_tempo(y, sr),
        "chromagram": _extract_chromagram(y, sr),
        "key_detection": _detect_key_placeholder(),
    }


# ── Feature extractors ────────────────────────────────────────────────────────

def _load_audio(file_path: Path):
    """
    Load audio into a numpy array with librosa.

    mono=True  – mix down to single channel (simpler feature extraction)
    sr=None    – honour the file's native sample rate first,
                 then resample to settings.SAMPLE_RATE
    """
    try:
        y, sr = librosa.load(
            str(file_path),
            sr=settings.SAMPLE_RATE,
            mono=True,
        )
        logger.debug("Loaded audio: %d samples @ %d Hz", len(y), sr)
        return y, sr
    except Exception as exc:
        logger.exception("librosa failed to load %s", file_path)
        raise HTTPException(
            status_code=422,
            detail=f"Could not decode audio file: {exc}",
        ) from exc


def _get_duration(y: np.ndarray, sr: int) -> float:
    """Return track duration rounded to two decimal places."""
    duration = librosa.get_duration(y=y, sr=sr)
    return round(float(duration), 2)


def _extract_tempo(y: np.ndarray, sr: int) -> float:
    """
    Estimate the global tempo (BPM) using librosa's beat tracker.

    beat_track returns an array; we take the first element and round it.
    """
    try:
        tempo, _ = librosa.beat.beat_track(
            y=y,
            sr=sr,
            hop_length=settings.HOP_LENGTH,
        )
        # librosa ≥0.10 returns an ndarray even for a single value
        bpm = float(np.atleast_1d(tempo)[0])
        logger.debug("Estimated tempo: %.2f BPM", bpm)
        return round(bpm, 2)
    except Exception as exc:
        logger.warning("Tempo extraction failed: %s", exc)
        raise HTTPException(status_code=500, detail="Tempo extraction failed.") from exc


def _extract_chromagram(y: np.ndarray, sr: int) -> dict:
    """
    Compute a chroma feature matrix and average it over time.

    The result is one energy value per pitch class (C … B),
    normalised to [0, 1] so values are easy to compare across tracks.
    """
    try:
        chroma = librosa.feature.chroma_stft(
            y=y,
            sr=sr,
            hop_length=settings.HOP_LENGTH,
            n_chroma=settings.N_CHROMA,
        )
        # Average across all time frames → shape (12,)
        mean_energy = chroma.mean(axis=1)

        # Normalise to [0, 1] (guard against all-zero edge case)
        max_val = mean_energy.max()
        if max_val > 0:
            mean_energy = mean_energy / max_val

        return {
            "pitch_classes": PITCH_CLASSES,
            "mean_energy": [round(float(v), 4) for v in mean_energy],
        }
    except Exception as exc:
        logger.warning("Chromagram extraction failed: %s", exc)
        raise HTTPException(status_code=500, detail="Chromagram extraction failed.") from exc


def _detect_key_placeholder() -> dict:
    """
    Key detection placeholder – not yet implemented.

    A future version could use the Krumhansl-Schmuckler key-finding
    algorithm or a neural model trained on the RWC dataset.
    """
    return {
        "key": None,
        "confidence": None,
        "note": "Key detection is not yet implemented.",
    }
