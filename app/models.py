"""
TuneMetrics – Pydantic Response Models
----------------------------------------
These models define the shape of every JSON response the API returns.
FastAPI uses them for automatic validation and OpenAPI documentation.
"""

from typing import Optional
from pydantic import BaseModel, Field


# ── Health check ──────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")
    app: str = Field(..., example="TuneMetrics")
    version: str = Field(..., example="0.1.0")


# ── Audio analysis ────────────────────────────────────────────────────────────

class ChromagramResult(BaseModel):
    """
    A chromagram maps audio energy onto the 12 pitch classes
    (C, C#, D, … B) averaged across the whole file.
    """
    pitch_classes: list[str] = Field(
        ...,
        description="Names of the 12 chromatic pitch classes",
        example=["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    )
    mean_energy: list[float] = Field(
        ...,
        description="Mean chroma energy per pitch class (same order as pitch_classes)",
    )


class KeyDetectionResult(BaseModel):
    """Placeholder – full implementation coming in v0.2."""
    key: Optional[str] = Field(None, example=None)
    confidence: Optional[float] = Field(None, example=None)
    note: str = Field(
        "Key detection is not yet implemented.",
        description="Human-readable status message",
    )


class AnalysisResponse(BaseModel):
    filename: str = Field(..., example="my_song.mp3")
    duration_seconds: float = Field(..., example=212.4)
    tempo_bpm: float = Field(..., example=128.0)
    chromagram: ChromagramResult
    key_detection: KeyDetectionResult


# ── Error responses ───────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    error: str = Field(..., example="Unsupported file type")
    detail: Optional[str] = Field(None, example="Only .mp3 and .wav files are accepted.")
