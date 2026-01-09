from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, DECIMAL, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    s3_url = Column(String(500), nullable=False)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="uploaded")
    file_size = Column(Integer)
    duration = Column(Float, nullable=True)
    frame_count = Column(Integer, nullable=True)

    # Relationships
    inferences = relationship("Inference", back_populates="video", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="video", uselist=False, cascade="all, delete-orphan")


class Inference(Base):
    __tablename__ = "inferences"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    frame_number = Column(Integer)
    frame_url = Column(String(500))
    damage_type = Column(String(100), index=True)
    severity = Column(String(50))
    confidence = Column(Float)
    bounding_box = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    video = relationship("Video", back_populates="inferences")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), unique=True, nullable=False)
    total_estimated_cost = Column(DECIMAL(10, 2))
    damage_summary = Column(JSON)
    pdf_url = Column(String(500))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    video = relationship("Video", back_populates="report")
