"""
File upload router
Handles video and image uploads
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Video
from app.schemas import UploadResponse
from app.utils.s3 import s3_client
from app.utils.file_validation import validate_file_extension, validate_file_size, is_video_file, is_image_file
from ml.video_processor import VideoProcessor, process_image_to_frame
import logging
import os
import tempfile
import uuid
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize video processor
video_processor = VideoProcessor(keyframe_interval=2.0)


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a video or image file for damage assessment

    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded file (video or image)
        db: Database session

    Returns:
        UploadResponse with video_id and file details

    Raises:
        HTTPException: If file validation fails or upload error occurs
    """
    logger.info(f"Receiving file upload: {file.filename}")

    # Validate file extension
    is_valid, message = validate_file_extension(file.filename)
    if not is_valid:
        logger.warning(f"Invalid file extension: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Read file content
    try:
        file_content = await file.read()
        file_size = len(file_content)
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading uploaded file"
        )

    # Validate file size
    is_valid, message = validate_file_size(file_size)
    if not is_valid:
        logger.warning(f"Invalid file size: {file_size} bytes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Upload to S3 or local storage
    try:
        s3_url = s3_client.upload_file_object(
            file_content=file_content,
            filename=unique_filename,
            folder="videos"
        )
        logger.info(f"File uploaded successfully to: {s3_url}")
    except Exception as e:
        logger.error(f"Error uploading to storage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file to storage"
        )

    # Determine if file is video or image
    file_is_video = is_video_file(file.filename)

    # Create database record
    try:
        video = Video(
            filename=file.filename,
            s3_url=s3_url,
            status="uploaded",
            file_size=file_size,
            duration=None if not file_is_video else 0.0,  # Will be updated during processing
            frame_count=1 if not file_is_video else None  # Images have 1 frame
        )
        db.add(video)
        db.commit()
        db.refresh(video)

        logger.info(f"Created database record for video_id: {video.id}")

        # Start background processing for videos
        # Images will be processed too (as single frame)
        from app.background_tasks import process_video_task
        background_tasks.add_task(process_video_task, video.id)
        logger.info(f"Added background task to process video_id: {video.id}")

        return UploadResponse(
            video_id=video.id,
            filename=file.filename,
            s3_url=s3_url,
            status=video.status,
            message="File uploaded successfully. Processing started."
        )

    except Exception as e:
        logger.error(f"Error creating database record: {e}")
        # Try to clean up uploaded file
        try:
            s3_client.delete_file(s3_url)
        except:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving file metadata"
        )


@router.get("/upload/status/{video_id}")
async def get_upload_status(
    video_id: int,
    db: Session = Depends(get_db)
):
    """
    Get upload status for a video

    Args:
        video_id: ID of the video
        db: Database session

    Returns:
        Upload status information
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with id {video_id} not found"
        )

    return {
        "video_id": video.id,
        "filename": video.filename,
        "status": video.status,
        "upload_timestamp": video.upload_timestamp,
        "file_size": video.file_size,
        "frame_count": video.frame_count
    }


@router.get("/videos")
async def list_videos(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List all uploaded videos with their status

    Args:
        limit: Maximum number of videos to return (default: 50)
        offset: Number of videos to skip (default: 0)
        db: Database session

    Returns:
        List of videos with their details
    """
    from app.models import Inference
    from sqlalchemy import func

    # Get videos with inference count
    videos = (
        db.query(
            Video,
            func.count(Inference.id).label('inference_count')
        )
        .outerjoin(Inference, Video.id == Inference.video_id)
        .group_by(Video.id)
        .order_by(Video.upload_timestamp.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    # Format response
    result = []
    for video, inference_count in videos:
        result.append({
            "video_id": video.id,
            "filename": video.filename,
            "status": video.status,
            "upload_timestamp": video.upload_timestamp,
            "file_size": video.file_size,
            "duration": video.duration,
            "frame_count": video.frame_count,
            "inference_count": inference_count
        })

    total_count = db.query(Video).count()

    return {
        "videos": result,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }


@router.delete("/upload/{video_id}")
async def delete_upload(
    video_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an uploaded file and its database record

    Args:
        video_id: ID of the video to delete
        db: Database session

    Returns:
        Success message
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with id {video_id} not found"
        )

    # Delete file from storage
    try:
        s3_client.delete_file(video.s3_url)
        logger.info(f"Deleted file from storage: {video.s3_url}")
    except Exception as e:
        logger.warning(f"Error deleting file from storage: {e}")

    # Delete database record (cascade will delete related inferences and reports)
    db.delete(video)
    db.commit()

    logger.info(f"Deleted video_id: {video_id}")

    return {
        "message": "Upload deleted successfully",
        "video_id": video_id
    }
