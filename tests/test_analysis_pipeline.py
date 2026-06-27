"""
Test script for complete damage analysis pipeline
Tests upload → processing → analysis workflow
"""
import requests
import time
import sys
from PIL import Image
import io

BASE_URL = "http://localhost:8000"


def create_test_image_bytes(width=800, height=600):
    """Create test image in memory"""
    # Create simple test image with colored rectangles
    img = Image.new('RGB', (width, height), color=(200, 200, 200))

    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=85)
    img_bytes.seek(0)

    return img_bytes


def print_separator(title=""):
    """Print formatted separator"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    else:
        print('='*60)


def test_complete_pipeline():
    """Test the complete analysis pipeline"""

    print_separator("AdjustR - Complete Analysis Pipeline Test")

    # Step 1: Upload image
    print("\n1️⃣  Uploading test image...")

    test_image = create_test_image_bytes()
    files = {'file': ('test_damage.jpg', test_image, 'image/jpeg')}

    try:
        response = requests.post(f"{BASE_URL}/api/upload", files=files)

        if response.status_code != 201:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.json())
            return None

        upload_data = response.json()
        video_id = upload_data['video_id']

        print(f"✅ Upload successful!")
        print(f"   Video ID: {video_id}")
        print(f"   Status: {upload_data['status']}")

    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

    # Step 2: Wait for processing (frame extraction)
    print("\n2️⃣  Waiting for frame extraction...")

    max_wait = 30
    start_time = time.time()
    processing_complete = False

    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/api/upload/status/{video_id}")

            if response.status_code == 200:
                status_data = response.json()
                current_status = status_data['status']

                print(f"   Status: {current_status}", end='\r')

                if current_status == "processed":
                    processing_complete = True
                    print(f"\n✅ Frame extraction complete!")
                    print(f"   Frames extracted: {status_data.get('frame_count', 0)}")
                    break
                elif current_status == "error":
                    print(f"\n❌ Processing failed!")
                    return None
        except Exception as e:
            print(f"\n❌ Error checking status: {e}")
            return None

        time.sleep(1)

    if not processing_complete:
        print(f"\n❌ Processing timed out")
        return None

    # Step 3: Trigger damage analysis
    print("\n3️⃣  Triggering damage analysis...")

    try:
        response = requests.post(f"{BASE_URL}/api/analyze/{video_id}")

        if response.status_code != 200:
            print(f"❌ Analysis trigger failed: {response.status_code}")
            print(response.json())
            return None

        analysis_data = response.json()

        print(f"✅ Analysis started!")
        print(f"   Message: {analysis_data.get('message', '')}")

    except Exception as e:
        print(f"❌ Analysis trigger error: {e}")
        return None

    # Step 4: Wait for analysis to complete
    print("\n4️⃣  Waiting for damage analysis...")

    start_time = time.time()
    analysis_complete = False

    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/api/analyze/status/{video_id}")

            if response.status_code == 200:
                status_data = response.json()
                current_status = status_data['status']

                print(f"   Status: {current_status}", end='\r')

                if current_status == "analyzed":
                    analysis_complete = True
                    print(f"\n✅ Analysis complete!")
                    break
                elif current_status == "error":
                    print(f"\n❌ Analysis failed!")
                    return None
        except Exception as e:
            print(f"\n❌ Error checking analysis: {e}")
            return None

        time.sleep(1)

    if not analysis_complete:
        print(f"\n❌ Analysis timed out")
        return None

    # Step 5: Get analysis results
    print("\n5️⃣  Fetching analysis results...")

    try:
        response = requests.get(f"{BASE_URL}/api/analyze/status/{video_id}")

        if response.status_code == 200:
            results = response.json()

            print(f"✅ Results retrieved!")
            print(f"\n📊 Analysis Summary:")
            print(f"   Video ID: {results['video_id']}")
            print(f"   Status: {results['status']}")
            print(f"   Frames analyzed: {results['frame_count']}")
            print(f"   Total detections: {results['total_inferences']}")
            print(f"   Estimated cost: ${results['total_estimated_cost']:.2f}")

            if results['damage_counts']:
                print(f"\n   Damage Types Detected:")
                for damage_type, count in results['damage_counts'].items():
                    print(f"      • {damage_type}: {count} instance(s)")
            else:
                print(f"\n   ℹ️  No damage detected in this image")
                print(f"      (YOLOv8 detects known objects; synthetic images may not trigger detections)")

            print(f"\n   Severity Breakdown:")
            for severity, count in results['severity_counts'].items():
                print(f"      • {severity.capitalize()}: {count}")

            return video_id
        else:
            print(f"❌ Failed to get results: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Error getting results: {e}")
        return None


def test_with_real_image(image_path):
    """Test pipeline with user-provided image"""

    print_separator(f"Testing with: {image_path}")

    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return

    print("\n1️⃣  Uploading image...")

    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}

        try:
            response = requests.post(f"{BASE_URL}/api/upload", files=files)

            if response.status_code != 201:
                print(f"❌ Upload failed: {response.status_code}")
                return

            upload_data = response.json()
            video_id = upload_data['video_id']

            print(f"✅ Uploaded! Video ID: {video_id}")

        except Exception as e:
            print(f"❌ Upload error: {e}")
            return

    # Wait for processing
    print("\n2️⃣  Waiting for processing...")
    time.sleep(3)

    # Check status
    response = requests.get(f"{BASE_URL}/api/upload/status/{video_id}")
    if response.status_code == 200 and response.json()['status'] == 'processed':
        print("✅ Processed!")

        # Trigger analysis
        print("\n3️⃣  Starting analysis...")
        requests.post(f"{BASE_URL}/api/analyze/{video_id}")

        # Wait for analysis
        time.sleep(5)

        # Get results
        print("\n4️⃣  Fetching results...")
        response = requests.get(f"{BASE_URL}/api/analyze/status/{video_id}")

        if response.status_code == 200:
            results = response.json()

            print(f"\n📊 Results:")
            print(f"   Total detections: {results['total_inferences']}")
            print(f"   Estimated cost: ${results['total_estimated_cost']:.2f}")

            if results['damage_counts']:
                print(f"\n   Detected damage:")
                for dtype, count in results['damage_counts'].items():
                    print(f"      • {dtype}: {count}x")


def run_tests():
    """Run all pipeline tests"""

    # Check backend health
    print("🔍 Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Backend is not running!")
            print("Please start with: docker-compose up")
            return
        print("✅ Backend is running\n")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("Please start with: docker-compose up")
        return

    # Test with synthetic image
    video_id = test_complete_pipeline()

    if video_id:
        print_separator("Test Summary")
        print(f"\n✅ Pipeline test completed successfully!")
        print(f"\n📝 What happened:")
        print(f"   1. Image uploaded → video_id: {video_id}")
        print(f"   2. Frames extracted (for images: 1 frame)")
        print(f"   3. YOLOv8 detection run on each frame")
        print(f"   4. Inferences stored in database")
        print(f"   5. Results available via API")

        print(f"\n💡 To test with your own image:")
        print(f"   python test_analysis_pipeline.py path/to/image.jpg")

        print(f"\n🗑️  To clean up test data:")
        print(f"   curl -X DELETE {BASE_URL}/api/upload/{video_id}")
    else:
        print("\n❌ Pipeline test failed")

    print_separator()


if __name__ == "__main__":
    import os

    if len(sys.argv) > 1:
        # Test with user image
        test_with_real_image(sys.argv[1])
    else:
        # Run standard tests
        run_tests()
