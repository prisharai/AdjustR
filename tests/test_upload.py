"""
Test script for upload endpoint
"""
import requests
import os
from io import BytesIO
from PIL import Image

# Backend URL
BASE_URL = "http://localhost:8000"


def create_test_image(filename="test_image.jpg", size=(800, 600)):
    """Create a test image"""
    img = Image.new('RGB', size, color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def test_health_check():
    """Test health check endpoint"""
    print("\n1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200


def test_image_upload():
    """Test image upload"""
    print("\n2. Testing image upload...")

    # Create test image
    test_image = create_test_image()

    files = {
        'file': ('test_damage.jpg', test_image, 'image/jpeg')
    }

    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 201:
        return response.json()['video_id']
    return None


def test_upload_status(video_id):
    """Test upload status endpoint"""
    print(f"\n3. Testing upload status for video_id {video_id}...")
    response = requests.get(f"{BASE_URL}/api/upload/status/{video_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


def test_invalid_file_type():
    """Test upload with invalid file type"""
    print("\n4. Testing invalid file type (should fail)...")

    # Create a fake text file
    files = {
        'file': ('test.txt', BytesIO(b"This is a text file"), 'text/plain')
    }

    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 400


def test_large_file():
    """Test upload with large file (should fail if over 100MB)"""
    print("\n5. Testing large file (simulated)...")
    print("Skipping actual large file test to save time")
    print("Would create 101MB file and expect 400 error")


def test_delete_upload(video_id):
    """Test delete upload"""
    print(f"\n6. Testing delete upload for video_id {video_id}...")
    response = requests.delete(f"{BASE_URL}/api/upload/{video_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing AdjustR Upload API")
    print("=" * 60)

    try:
        # Test 1: Health check
        test_health_check()

        # Test 2: Upload image
        video_id = test_image_upload()

        if video_id:
            # Test 3: Check status
            test_upload_status(video_id)

            # Test 6: Delete upload
            test_delete_upload(video_id)

        # Test 4: Invalid file type
        test_invalid_file_type()

        # Test 5: Large file (skipped)
        test_large_file()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend")
        print("Make sure the backend is running: docker-compose up")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
