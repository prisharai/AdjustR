"""
Background task processing
Handles video processing and damage analysis after upload
"""
from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src.db.models import Video, Inference
from src.utils.storage import s3_client
from src.ml.video_processor import VideoProcessor, process_image_to_frame
from src.ml.detector import get_damage_detector
import logging
import tempfile
import os
import shutil
import time

logger = logging.getLogger(__name__)


def process_video_task(video_id: int):
    """
    Background task to process uploaded video

    Args:
        video_id: ID of video to process
    """
    logger.info(f"Starting background processing for video_id: {video_id}")

    # Create new database session for background task
    db = SessionLocal()

    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == video_id).first()

        if not video:
            logger.error(f"Video {video_id} not found in database")
            return

        # Update status to processing
        video.status = "processing"
        db.commit()

        logger.info(f"Processing video: {video.filename}")

        # Download video to temp location
        temp_dir = tempfile.mkdtemp(prefix=f"adjustr_video_{video_id}_")
        temp_video_path = os.path.join(temp_dir, "video_temp")

        try:
            # Download from S3/local storage
            s3_client.download_file(video.s3_url, temp_video_path)
            logger.info(f"Downloaded video to: {temp_video_path}")

            # Determine if video or image
            is_video = video.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))

            if is_video:
                # Process video - extract keyframes
                processor = VideoProcessor(keyframe_interval=2.0)

                frame_paths, duration, frame_count = processor.process_video_file(
                    video_path=temp_video_path,
                    video_id=video_id
                )

                logger.info(f"Extracted {frame_count} frames, duration: {duration:.2f}s")

                # Upload frames to S3/local storage
                frame_urls = []
                for i, frame_path in enumerate(frame_paths):
                    frame_filename = f"frame_{i:04d}.jpg"
                    frame_url = s3_client.upload_file(
                        file_path=frame_path,
                        object_name=f"video_{video_id}_{frame_filename}",
                        folder="frames"
                    )
                    frame_urls.append(frame_url)
                    logger.debug(f"Uploaded frame {i}: {frame_url}")

                # Update video record
                video.duration = duration
                video.frame_count = frame_count
                video.status = "processed"

            else:
                # Process image - treat as single frame
                frame_output_dir = os.path.join(temp_dir, "frames")
                frame_paths, frame_count = process_image_to_frame(
                    image_path=temp_video_path,
                    output_dir=frame_output_dir,
                    video_id=video_id
                )

                logger.info(f"Processed image as {frame_count} frame")

                # Upload frame to S3/local storage
                frame_url = s3_client.upload_file(
                    file_path=frame_paths[0],
                    object_name=f"video_{video_id}_frame_0000.jpg",
                    folder="frames"
                )

                logger.info(f"Uploaded frame: {frame_url}")

                # Update video record
                video.duration = 0.0
                video.frame_count = frame_count
                video.status = "processed"

            db.commit()

            logger.info(f"✅ Video {video_id} processed successfully - Status: {video.status}")

        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")

            # Update status to error
            video.status = "error"
            db.commit()

            raise

        finally:
            # Clean up temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temp directory: {temp_dir}")

    except Exception as e:
        logger.error(f"Background task failed for video {video_id}: {e}")

    finally:
        db.close()
