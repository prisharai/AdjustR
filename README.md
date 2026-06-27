# AdjustR

Backend API for automated property damage assessment using computer vision.

Analyzes images and video footage to detect and classify property damage, producing structured reports with damage type, severity, and repair cost estimates.

## How it works

1. Upload images or video of a property
2. The pipeline extracts frames and runs NVIDIA [LocateAnything-3B](https://huggingface.co/nvidia/LocateAnything-3B) — an open-set vision-language grounding model — to locate damage regions via natural language queries
3. Each detection is classified by damage type and severity, with a cost estimate attached
4. Results are stored in PostgreSQL and exposed via a REST API

## Stack

- **API**: FastAPI + SQLAlchemy
- **Vision model**: `nvidia/LocateAnything-3B` (Transformers pipeline)
- **Database**: PostgreSQL with Alembic migrations
- **Storage**: AWS S3 or local fallback

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env  # fill in your values
alembic upgrade head

uvicorn src.api.main:app --reload
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload image or video |
| GET | `/api/upload/status/{id}` | Check processing status |
| POST | `/api/analyze/{id}` | Trigger damage analysis |
| GET | `/api/results/{id}` | Get detection results |
| GET | `/health` | Health check |

## License

LocateAnything-3B is released under the NVIDIA non-commercial license. This project is for research and educational use only.
