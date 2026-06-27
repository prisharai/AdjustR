from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.database import engine, Base
from src.api.routers import upload, analysis
from src.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AdjustR", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
