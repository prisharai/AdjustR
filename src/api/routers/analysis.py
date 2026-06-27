"""
Analysis router
Handles damage analysis for uploaded videos
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Video, Inference
from src.api.schemas import AnalysisResponse, ResultsResponse, VideoMetadata, InferenceDetail
from src.ml.detector import get_damage_detector
from src.ml.damage_mapping import get_damage_cost
import logging
import os
from typing import List, Dict, Optional
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze/{video_id}", response_model=AnalysisResponse)
async def analyze_video(
    video_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger damage analysis for a processed video

    This endpoint starts the analysis process which runs in the background.
    The video must be in 'processed' status (frames extracted).

    Args:
        video_id: ID of the video to analyze
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        AnalysisResponse with initial status

    Raises:
        HTTPException: If video not found or not ready for analysis
    """
    logger.info(f"Analysis requested for video_id: {video_id}")

    # Get video from database
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with id {video_id} not found"
        )

    # Check if video is ready for analysis
    if video.status != "processed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Video must be in 'processed' status. Current status: {video.status}"
        )

    # Check if already analyzed
    existing_inferences = db.query(Inference).filter(Inference.video_id == video_id).count()
    if existing_inferences > 0:
        logger.warning(f"Video {video_id} already has {existing_inferences} inferences")
        # Re-analyze: delete old inferences
        db.query(Inference).filter(Inference.video_id == video_id).delete()
        db.commit()
        logger.info(f"Deleted {existing_inferences} old inferences for re-analysis")

    # Update status to analyzing
    video.status = "analyzing"
    db.commit()

    # Start background analysis task
    from src.api.background_tasks_analysis import analyze_video_task
    background_tasks.add_task(analyze_video_task, video_id)

    logger.info(f"Analysis task queued for video_id: {video_id}")

    return AnalysisResponse(
        video_id=video_id,
        total_damages=0,
        estimated_cost=0.0,
        damages=[],
        processing_time=0.0,
        message="Analysis started. Check status endpoint for progress."
    )


@router.get("/analyze/status/{video_id}")
async def get_analysis_status(
    video_id: int,
    db: Session = Depends(get_db)
):
    """
    Get analysis status and results

    Args:
        video_id: ID of the video
        db: Database session

    Returns:
        Analysis status and results if complete
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with id {video_id} not found"
        )

    # Get inferences
    inferences = db.query(Inference).filter(Inference.video_id == video_id).all()

    # Calculate total cost
    total_cost = sum(
        get_damage_cost(inf.damage_type, inf.severity)
        for inf in inferences
    )

    # Aggregate statistics
    damage_counts = {}
    severity_counts = {'low': 0, 'medium': 0, 'high': 0}

    for inf in inferences:
        # Count damage types
        if inf.damage_type not in damage_counts:
            damage_counts[inf.damage_type] = 0
        damage_counts[inf.damage_type] += 1

        # Count severities
        if inf.severity in severity_counts:
            severity_counts[inf.severity] += 1

    return {
        'video_id': video_id,
        'status': video.status,
        'total_inferences': len(inferences),
        'total_estimated_cost': float(total_cost),
        'damage_counts': damage_counts,
        'severity_counts': severity_counts,
        'frame_count': video.frame_count,
        'analysis_complete': video.status == 'analyzed'
    }


@router.get("/results/{video_id}", response_model=ResultsResponse)
async def get_results(
    video_id: int,
    damage_type: Optional[str] = Query(None, description="Filter by damage type"),
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high)"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    sort_by: Optional[str] = Query("frame_number", description="Sort by: frame_number, confidence, severity, damage_type"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive results for an analyzed video with filtering and sorting

    This endpoint returns complete video metadata, all inferences with details,
    and aggregated statistics. Uses optimized queries with eager loading.

    Query Parameters:
        - damage_type: Filter by specific damage type
        - severity: Filter by severity level (low, medium, high)
        - min_confidence: Only return inferences above this confidence threshold
        - sort_by: Sort results by field (frame_number, confidence, severity, damage_type)
        - sort_order: Sort order (asc or desc)

    Args:
        video_id: ID of the video
        db: Database session

    Returns:
        ResultsResponse with video metadata and filtered/sorted inference data

    Raises:
        HTTPException: If video not found or not analyzed
    """
    logger.info(f"Fetching results for video_id: {video_id} with filters: damage_type={damage_type}, severity={severity}, min_confidence={min_confidence}")

    # Optimized query with eager loading
    video = db.query(Video).options(
        joinedload(Video.inferences)
    ).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with id {video_id} not found"
        )

    # Get all inferences (already loaded via joinedload)
    inferences = video.inferences

    # Apply filters
    if damage_type:
        inferences = [inf for inf in inferences if inf.damage_type == damage_type]

    if severity:
        inferences = [inf for inf in inferences if inf.severity == severity]

    if min_confidence is not None:
        inferences = [inf for inf in inferences if inf.confidence >= min_confidence]

    # Apply sorting
    reverse_order = (sort_order.lower() == "desc")

    if sort_by == "confidence":
        inferences = sorted(inferences, key=lambda x: x.confidence, reverse=reverse_order)
    elif sort_by == "severity":
        severity_order = {'low': 1, 'medium': 2, 'high': 3}
        inferences = sorted(inferences, key=lambda x: severity_order.get(x.severity, 0), reverse=reverse_order)
    elif sort_by == "damage_type":
        inferences = sorted(inferences, key=lambda x: x.damage_type, reverse=reverse_order)
    else:  # Default: frame_number
        inferences = sorted(inferences, key=lambda x: x.frame_number, reverse=reverse_order)

    # Calculate total cost
    total_cost = sum(
        get_damage_cost(inf.damage_type, inf.severity)
        for inf in inferences
    )

    # Build damage summary
    damage_counts = {}
    severity_counts = {'low': 0, 'medium': 0, 'high': 0}
    frames_with_damage = set()

    for inf in inferences:
        # Count damage types
        if inf.damage_type not in damage_counts:
            damage_counts[inf.damage_type] = {
                'count': 0,
                'avg_confidence': 0.0,
                'severities': {'low': 0, 'medium': 0, 'high': 0}
            }
        damage_counts[inf.damage_type]['count'] += 1
        damage_counts[inf.damage_type]['severities'][inf.severity] += 1

        # Count severities
        if inf.severity in severity_counts:
            severity_counts[inf.severity] += 1

        # Track unique frames
        frames_with_damage.add(inf.frame_number)

    # Calculate average confidence per damage type
    for damage_type in damage_counts:
        damages_of_type = [inf for inf in inferences if inf.damage_type == damage_type]
        avg_conf = sum(d.confidence for d in damages_of_type) / len(damages_of_type)
        damage_counts[damage_type]['avg_confidence'] = round(avg_conf, 3)

    # Build comprehensive summary
    damage_summary = {
        'total_inferences': len(inferences),
        'total_estimated_cost': float(total_cost),
        'unique_damage_types': len(damage_counts),
        'frames_with_damage': len(frames_with_damage),
        'total_frames': video.frame_count or 0,
        'damage_counts': damage_counts,
        'severity_counts': severity_counts,
        'avg_confidence': round(
            sum(inf.confidence for inf in inferences) / len(inferences), 3
        ) if inferences else 0.0
    }

    logger.info(f"Results retrieved for video_id: {video_id} - {len(inferences)} inferences")

    return ResultsResponse(
        video=VideoMetadata.model_validate(video),
        inferences=[InferenceDetail.model_validate(inf) for inf in inferences],
        total_estimated_cost=float(total_cost),
        damage_summary=damage_summary
    )


@router.delete("/analyze/{video_id}")
async def delete_analysis(
    video_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete analysis results (inferences) for a video

    Args:
        video_id: ID of the video
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

    # Delete inferences
    deleted_count = db.query(Inference).filter(Inference.video_id == video_id).delete()
    db.commit()

    # Update video status
    if video.status == "analyzed":
        video.status = "processed"
        db.commit()

    logger.info(f"Deleted {deleted_count} inferences for video_id: {video_id}")

    return {
        'message': f'Deleted {deleted_count} inferences',
        'video_id': video_id
    }
