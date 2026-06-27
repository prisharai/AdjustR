"""
Test script for video processing
Creates test video and tests keyframe extraction
"""
import cv2
import numpy as np
import os
import tempfile
import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"


def create_test_video(filename="test_video.mp4", duration=5, fps=30):
    """
    Create a test video with colored frames

    Args:
        filename: Output filename
        duration: Duration in seconds
        fps: Frames per second

    Returns:
        Path to created video
    """
    print(f"\n📹 Creating test video: {filename}")

    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    total_frames = duration * fps

    for i in range(total_frames):
        # Create frame with changing color
        # Red -> Green -> Blue -> Red
        ratio = i / total_frames
        if ratio < 0.33:
            color = (0, 0, 255)  # Red
        elif ratio < 0.66:
            color = (0, 255, 0)  # Green
        else:
            color = (255, 0, 0)  # Blue

        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = color

        # Add frame number text
        cv2.putText(
            frame,
            f"Frame {i}/{total_frames}",
            (50, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        out.write(frame)

    out.release()

    file_size = os.path.getsize(filename) / 1024 / 1024
    print(f"✓ Created video: {filename} ({file_size:.2f} MB)")
    print(f"  Duration: {duration}s, FPS: {fps}, Total frames: {total_frames}")

    return filename


def test_video_upload_and_processing():
    """Test video upload and background processing"""
    print("\n" + "=" * 60)
    print("Testing Video Processing Pipeline")
    print("=" * 60)

    # Create test video
    test_video = create_test_video("test_damage_video.mp4", duration=5, fps=30)

    try:
        # Upload video
        print("\n1. Uploading video...")
        with open(test_video, 'rb') as f:
            files = {'file': (test_video, f, 'video/mp4')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)

        if response.status_code != 201:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.json())
            return

        upload_data = response.json()
        video_id = upload_data['video_id']

        print(f"✓ Upload successful!")
        print(f"  Video ID: {video_id}")
        print(f"  Status: {upload_data['status']}")
        print(f"  Message: {upload_data['message']}")

        # Poll for processing completion
        print("\n2. Waiting for processing to complete...")
        max_wait = 30  # seconds
        start_time = time.time()
        processing_complete = False

        while time.time() - start_time < max_wait:
            response = requests.get(f"{BASE_URL}/api/upload/status/{video_id}")

            if response.status_code != 200:
                print(f"❌ Failed to get status: {response.status_code}")
                break

            status_data = response.json()
            current_status = status_data['status']

            print(f"  Status: {current_status}", end='\r')

            if current_status == "processed":
                processing_complete = True
                break
            elif current_status == "error":
                print(f"\n❌ Processing failed!")
                break

            time.sleep(1)

        print()  # New line after status updates

        if processing_complete:
            print("✓ Processing complete!")
            print(f"\n3. Processing results:")
            print(f"  Video ID: {status_data['video_id']}")
            print(f"  Filename: {status_data['filename']}")
            print(f"  Status: {status_data['status']}")
            print(f"  Duration: {status_data.get('duration', 'N/A')}s")
            print(f"  Frame count: {status_data.get('frame_count', 'N/A')}")

            # Verify frames were created
            expected_frames = int(5 / 2)  # 5 second video, 2 second intervals
            actual_frames = status_data.get('frame_count', 0)

            print(f"\n4. Frame extraction verification:")
            print(f"  Expected frames (approx): {expected_frames}")
            print(f"  Actual frames extracted: {actual_frames}")

            if actual_frames >= expected_frames - 1:  # Allow for rounding
                print("  ✓ Frame extraction looks good!")
            else:
                print("  ⚠️  Fewer frames than expected")

            # Check if frames are stored
            print(f"\n5. Storage verification:")
            print("  Frames should be stored in uploads/frames/ or S3")

            return video_id

        else:
            print("❌ Processing timed out or failed")
            return None

    finally:
        # Cleanup test video
        if os.path.exists(test_video):
            os.remove(test_video)
            print(f"\n🧹 Cleaned up test file: {test_video}")


def test_image_processing():
    """Test image upload and processing"""
    print("\n" + "=" * 60)
    print("Testing Image Processing")
    print("=" * 60)

    # Create test image
    print("\n📷 Creating test image...")
    from PIL import Image

    img = Image.new('RGB', (800, 600), color=(255, 0, 0))
    test_image = "test_damage_image.jpg"
    img.save(test_image)

    print(f"✓ Created image: {test_image}")

    try:
        # Upload image
        print("\n1. Uploading image...")
        with open(test_image, 'rb') as f:
            files = {'file': (test_image, f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)

        if response.status_code != 201:
            print(f"❌ Upload failed: {response.status_code}")
            return

        upload_data = response.json()
        video_id = upload_data['video_id']

        print(f"✓ Upload successful!")
        print(f"  Video ID: {video_id}")

        # Wait for processing
        print("\n2. Waiting for processing...")
        time.sleep(3)

        # Check status
        response = requests.get(f"{BASE_URL}/api/upload/status/{video_id}")
        status_data = response.json()

        print(f"\n3. Processing results:")
        print(f"  Status: {status_data['status']}")
        print(f"  Frame count: {status_data.get('frame_count', 'N/A')}")

        if status_data.get('frame_count') == 1:
            print("  ✓ Image processed correctly as single frame")
        else:
            print("  ⚠️  Unexpected frame count for image")

    finally:
        # Cleanup
        if os.path.exists(test_image):
            os.remove(test_image)
            print(f"\n🧹 Cleaned up test file: {test_image}")


def run_all_tests():
    """Run all video processing tests"""
    try:
        # Test health check first
        print("0. Checking backend health...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Backend is not running!")
            print("Please start with: docker-compose up")
            return

        print("✓ Backend is running\n")

        # Test video processing
        video_id = test_video_upload_and_processing()

        # Test image processing
        test_image_processing()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)

        if video_id:
            print(f"\nℹ️  To check stored frames:")
            print(f"   docker exec -it adjustr-backend ls -lh uploads/frames/")
            print(f"\nℹ️  To clean up test data:")
            print(f"   curl -X DELETE {BASE_URL}/api/upload/{video_id}")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend")
        print("Make sure the backend is running: docker-compose up")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
