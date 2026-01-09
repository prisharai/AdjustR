"""
Background task for damage analysis
Separate file to avoid circular imports
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Video, Inference
from app.utils.s3 import s3_client
from ml.damage_detector import get_damage_detector
import logging
import tempfile
import os
import time

logger = logging.getLogger(__name__)


def analyze_video_task(video_id: int):
    """
    Background task to analyze video frames for damage

    Args:
        video_id: ID of video to analyze
    """
    logger.info(f"Starting damage analysis for video_id: {video_id}")
    start_time = time.time()

    # Create new database session for background task
    db = SessionLocal()

    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == video_id).first()

        if not video:
            logger.error(f"Video {video_id} not found in database")
            return

        # Verify video is in correct status
        if video.status != "analyzing":
            logger.warning(f"Video {video_id} status is '{video.status}', expected 'analyzing'")

        logger.info(f"Analyzing {video.frame_count} frames for video: {video.filename}")

        # Initialize damage detector
        detector = get_damage_detector()

        # Get list of frame URLs for this video
        # Frames are stored as: uploads/frames/video_{video_id}_frame_{num}.jpg
        frame_paths = []
        temp_dir = tempfile.mkdtemp(prefix=f"analysis_{video_id}_")

        try:
            # Download frames from S3/local storage
            for frame_num in range(video.frame_count):
                frame_filename = f"video_{video_id}_frame_{frame_num:04d}.jpg"
                frame_s3_path = f"/uploads/frames/{frame_filename}"

                # Download to temp location
                temp_frame_path = os.path.join(temp_dir, frame_filename)

                try:
                    s3_client.download_file(frame_s3_path, temp_frame_path)
                    frame_paths.append(temp_frame_path)
                    logger.debug(f"Downloaded frame {frame_num}: {frame_filename}")
                except Exception as e:
                    logger.warning(f"Could not download frame {frame_num}: {e}")
                    continue

            logger.info(f"Downloaded {len(frame_paths)} frames for analysis")

            # Run batch detection on all frames
            total_detections = 0

            for frame_num, frame_path in enumerate(frame_paths):
                try:
                    # Run detection
                    detections = detector.detect_damage(
                        image_path=frame_path,
                        confidence_threshold=0.25
                    )

                    logger.debug(f"Frame {frame_num}: {len(detections)} detections")

                    # Store each detection as inference
                    for detection in detections:
                        inference = Inference(
                            video_id=video_id,
                            frame_number=frame_num,
                            frame_url=f"/uploads/frames/video_{video_id}_frame_{frame_num:04d}.jpg",
                            damage_type=detection['damage_type'],
                            severity=detection['severity'],
                            confidence=detection['confidence'],
                            bounding_box=detection['bounding_box']
                        )
                        db.add(inference)
                        total_detections += 1

                    # Commit every few frames to avoid memory issues
                    if frame_num % 10 == 0:
                        db.commit()

                except Exception as e:
                    logger.error(f"Error analyzing frame {frame_num}: {e}")
                    continue

            # Final commit
            db.commit()

            # Update video status
            video.status = "analyzed"
            db.commit()

            processing_time = time.time() - start_time

            logger.info(f"✅ Analysis complete for video {video_id}")
            logger.info(f"   Total detections: {total_detections}")
            logger.info(f"   Frames analyzed: {len(frame_paths)}")
            logger.info(f"   Processing time: {processing_time:.2f}s")
            logger.info(f"   Status: {video.status}")

        except Exception as e:
            logger.error(f"Error during frame analysis: {e}")
            video.status = "error"
            db.commit()
            raise

        finally:
            # Clean up temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temp directory: {temp_dir}")

    except Exception as e:
        logger.error(f"Analysis task failed for video {video_id}: {e}")
        import traceback
        traceback.print_exc()

        # Update status to error
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                video.status = "error"
                db.commit()
        except:
            pass

    finally:
        db.close()
