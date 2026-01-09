from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


# Upload Schemas
class UploadResponse(BaseModel):
    video_id: int
    filename: str
    s3_url: str
    status: str
    message: str

    class Config:
        from_attributes = True


# Video Schemas
class VideoBase(BaseModel):
    filename: str


class VideoMetadata(VideoBase):
    id: int
    s3_url: str
    upload_timestamp: datetime
    status: str
    file_size: Optional[int]
    duration: Optional[float]
    frame_count: Optional[int]

    class Config:
        from_attributes = True


# Inference Schemas
class InferenceBase(BaseModel):
    frame_number: int
    damage_type: str
    severity: str
    confidence: float


class InferenceDetail(InferenceBase):
    id: int
    video_id: int
    frame_url: Optional[str]
    bounding_box: Optional[Dict]
    created_at: datetime

    class Config:
        from_attributes = True


# Analysis Schemas
class AnalysisResponse(BaseModel):
    video_id: int
    total_damages: int
    estimated_cost: float
    damages: List[InferenceDetail]
    processing_time: float
    message: Optional[str] = None

    class Config:
        from_attributes = True


# Results Schemas
class ResultsResponse(BaseModel):
    video: VideoMetadata
    inferences: List[InferenceDetail]
    total_estimated_cost: Optional[float]
    damage_summary: Optional[Dict]

    class Config:
        from_attributes = True


# Report Schemas
class ReportResponse(BaseModel):
    report_id: int
    video_id: int
    pdf_url: str
    generated_at: datetime

    class Config:
        from_attributes = True
