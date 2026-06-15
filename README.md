# 🎵 TuneMetrics

A production-ready FastAPI backend that accepts uploaded audio files and returns extracted music features — tempo (BPM), chromagram, and a placeholder for key detection.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Example Response](#example-response)
- [Running the Tests](#running-the-tests)
- [Configuration](#configuration)
- [Roadmap](#roadmap)

---

## Features

| Feature | Status |
|---|---|
| Upload `.mp3` / `.wav` files | ✅ |
| Tempo / BPM detection | ✅ |
| Chromagram (12 pitch classes) | ✅ |
| Key detection | 🔜 Placeholder |
| File-type & size validation | ✅ |
| Auto-cleanup of temp files | ✅ |
| OpenAPI docs (`/docs`) | ✅ |

---

## Project Structure

```
tunemetrics/
├── app/
│   ├── main.py              # FastAPI app, middleware, router registration
│   ├── config.py            # All settings in one place
│   ├── models.py            # Pydantic request/response models
│   ├── routes/
│   │   ├── health.py        # GET /health
│   │   └── analyze.py       # POST /analyze
│   ├── services/
│   │   └── audio_processor.py   # librosa feature extraction
│   └── utils/
│       └── file_utils.py    # Upload validation + temp-file helpers
├── tests/
│   └── test_endpoints.py    # pytest test suite
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone / download the project

```bash
git clone https://github.com/your-org/tunemetrics.git
cd tunemetrics
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note — macOS users:** librosa's audio loading relies on `soundfile` for WAV and `audioread` / `ffmpeg` for MP3.  
> Install ffmpeg with Homebrew if MP3 support is missing:
> ```bash
> brew install ffmpeg
> ```

### 4. Run the development server

```bash
uvicorn app.main:app --reload
```

The API is now live at **http://127.0.0.1:8000**.  
Interactive docs: **http://127.0.0.1:8000/docs**

---

## API Reference

### `GET /health`

Returns the app's liveness status.

**Response 200**
```json
{
  "status": "ok",
  "app": "TuneMetrics",
  "version": "0.1.0"
}
```

---

### `POST /analyze`

Upload an audio file and receive music feature data.

**Request** — `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | `UploadFile` | An `.mp3` or `.wav` audio file (max 50 MB) |

**cURL example**
```bash
curl -X POST http://127.0.0.1:8000/analyze \
     -F "file=@/path/to/your/song.mp3"
```

**Python (httpx) example**
```python
import httpx

with open("song.mp3", "rb") as f:
    r = httpx.post(
        "http://127.0.0.1:8000/analyze",
        files={"file": ("song.mp3", f, "audio/mpeg")},
    )
print(r.json())
```

**Error codes**

| Code | Reason |
|---|---|
| 400 | Unsupported file type or missing filename |
| 413 | File exceeds the 50 MB size limit |
| 422 | Audio could not be decoded by librosa |
| 500 | Unexpected internal error |

---

## Example Response

```json
{
  "filename": "my_track.mp3",
  "duration_seconds": 212.4,
  "tempo_bpm": 128.0,
  "chromagram": {
    "pitch_classes": ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"],
    "mean_energy": [0.8, 0.12, 0.55, 0.2, 0.93, 0.3, 0.7, 0.45, 0.6, 0.35, 0.25, 0.65]
  },
  "key_detection": {
    "key": null,
    "confidence": null,
    "note": "Key detection is not yet implemented."
  }
}
```

### Reading the chromagram

The `mean_energy` list contains one value per pitch class (C through B), normalised to **[0, 1]**.  
A high value (e.g. `0.93` for E) means that pitch class was energetically prominent throughout the track — useful for estimating the musical key.

---

## Running the Tests

```bash
pytest -v
```

The test suite mocks librosa so it runs **instantly** without real audio files.

---

## Configuration

All settings live in `app/config.py`.  No environment variables are required to run locally.

| Setting | Default | Description |
|---|---|---|
| `UPLOAD_DIR` | `tmp_uploads/` | Temporary storage for uploaded files |
| `ALLOWED_EXTENSIONS` | `.mp3`, `.wav` | Accepted file types |
| `MAX_FILE_SIZE_MB` | `50` | Upload size limit |
| `SAMPLE_RATE` | `22 050 Hz` | librosa resampling target |
| `HOP_LENGTH` | `512` | STFT hop size |
| `N_CHROMA` | `12` | Chroma bins |

---

## Roadmap

- [ ] **Key detection** — Krumhansl-Schmuckler key-finding algorithm
- [ ] **Spectral features** — spectral centroid, rolloff, zero-crossing rate
- [ ] **Beat grid** — return timestamps of individual beats
- [ ] **Async processing** — offload librosa to a thread pool for large files
- [ ] **Docker support** — `Dockerfile` + `docker-compose.yml`
- [ ] **Authentication** — API key middleware

---

## Licence

MIT — do whatever you like, just keep the attribution.
