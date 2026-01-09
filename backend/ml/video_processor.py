"""
Video processing module
Extracts keyframes from videos using OpenCV
"""
import cv2
import os
import tempfile
import logging
from typing import List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Process videos to extract keyframes"""

    def __init__(self, keyframe_interval: float = 2.0):
        """
        Initialize video processor

        Args:
            keyframe_interval: Interval in seconds between extracted frames
        """
        self.keyframe_interval = keyframe_interval

    def extract_keyframes(
        self,
        video_path: str,
        output_dir: str,
        frame_prefix: str = "frame"
    ) -> Tuple[List[str], float, int]:
        """
        Extract keyframes from video at regular intervals

        Args:
            video_path: Path to video file
            output_dir: Directory to save extracted frames
            frame_prefix: Prefix for frame filenames

        Returns:
            Tuple of (frame_paths, duration, total_frames)

        Raises:
            Exception: If video cannot be processed
        """
        logger.info(f"Processing video: {video_path}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Open video
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise Exception(f"Failed to open video: {video_path}")

        try:
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0

            logger.info(f"Video properties - FPS: {fps}, Total Frames: {total_frames}, Duration: {duration:.2f}s")

            # Calculate frame interval
            frame_interval = int(fps * self.keyframe_interval)
            if frame_interval < 1:
                frame_interval = 1

            extracted_frames = []
            frame_count = 0
            saved_count = 0

            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Extract frame at interval
                if frame_count % frame_interval == 0:
                    frame_filename = f"{frame_prefix}_{saved_count:04d}.jpg"
                    frame_path = os.path.join(output_dir, frame_filename)

                    # Save frame as JPEG
                    cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    extracted_frames.append(frame_path)

                    logger.debug(f"Extracted frame {saved_count} at {frame_count}/{total_frames}")
                    saved_count += 1

                frame_count += 1

            logger.info(f"Extracted {len(extracted_frames)} keyframes from video")

            return extracted_frames, duration, len(extracted_frames)

        except Exception as e:
            logger.error(f"Error extracting keyframes: {e}")
            raise

        finally:
            cap.release()

    def process_video_file(
        self,
        video_path: str,
        video_id: int
    ) -> Tuple[List[str], float, int]:
        """
        Process a video file and extract keyframes to temp directory

        Args:
            video_path: Path to video file
            video_id: Database video ID for organizing frames

        Returns:
            Tuple of (frame_paths, duration, frame_count)
        """
        # Create temp directory for frames
        temp_dir = tempfile.mkdtemp(prefix=f"video_{video_id}_")

        try:
            frame_paths, duration, frame_count = self.extract_keyframes(
                video_path=video_path,
                output_dir=temp_dir,
                frame_prefix=f"video_{video_id}_frame"
            )

            logger.info(f"Video {video_id} processed: {frame_count} frames, {duration:.2f}s duration")

            return frame_paths, duration, frame_count

        except Exception as e:
            logger.error(f"Failed to process video {video_id}: {e}")
            # Clean up temp directory on error
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise

    def get_video_info(self, video_path: str) -> dict:
        """
        Get video information without extracting frames

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video metadata
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise Exception(f"Failed to open video: {video_path}")

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0

            return {
                "fps": fps,
                "total_frames": total_frames,
                "width": width,
                "height": height,
                "duration": duration
            }

        finally:
            cap.release()

    def create_thumbnail(
        self,
        video_path: str,
        output_path: str,
        timestamp: float = 0.0
    ) -> str:
        """
        Create a thumbnail from video at specific timestamp

        Args:
            video_path: Path to video file
            output_path: Path to save thumbnail
            timestamp: Timestamp in seconds

        Returns:
            Path to saved thumbnail
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise Exception(f"Failed to open video: {video_path}")

        try:
            # Set position
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)

            ret, frame = cap.read()

            if not ret:
                raise Exception("Failed to read frame for thumbnail")

            # Save thumbnail
            cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])

            logger.info(f"Created thumbnail: {output_path}")

            return output_path

        finally:
            cap.release()


def process_image_to_frame(
    image_path: str,
    output_dir: str,
    video_id: int
) -> Tuple[List[str], int]:
    """
    Process an image file (treat as single frame)

    Args:
        image_path: Path to image file
        output_dir: Directory to save frame
        video_id: Database video ID

    Returns:
        Tuple of (frame_paths, frame_count)
    """
    os.makedirs(output_dir, exist_ok=True)

    # For images, just copy to output directory
    import shutil

    frame_filename = f"video_{video_id}_frame_0000.jpg"
    frame_path = os.path.join(output_dir, frame_filename)

    # Copy or convert image to JPEG
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise Exception(f"Failed to read image: {image_path}")

        cv2.imwrite(frame_path, img, [cv2.IMWRITE_JPEG_QUALITY, 85])

        logger.info(f"Processed image as single frame: {frame_path}")

        return [frame_path], 1

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise
