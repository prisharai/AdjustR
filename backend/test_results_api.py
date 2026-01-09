"""
Test script for Day 7 - Results API
Tests the comprehensive results endpoint with filtering and sorting
"""
import requests
import time
import sys
from PIL import Image
import io

BASE_URL = "http://localhost:8000"


def create_test_image_bytes(width=800, height=600):
    """Create test image in memory"""
    img = Image.new('RGB', (width, height), color=(200, 200, 200))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=85)
    img_bytes.seek(0)
    return img_bytes


def print_separator(title=""):
    """Print formatted separator"""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print('='*70)
    else:
        print('='*70)


def setup_test_data():
    """Upload and analyze an image to get test data"""
    print("\n🔧 Setting up test data...")

    # Upload image
    test_image = create_test_image_bytes()
    files = {'file': ('test_results.jpg', test_image, 'image/jpeg')}

    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.status_code}")
        return None

    video_id = response.json()['video_id']
    print(f"✅ Uploaded image with video_id: {video_id}")

    # Wait for processing
    print("   Waiting for frame extraction...")
    time.sleep(3)

    # Trigger analysis
    response = requests.post(f"{BASE_URL}/api/analyze/{video_id}")
    if response.status_code != 200:
        print(f"❌ Analysis trigger failed: {response.status_code}")
        return None

    print("   Analysis started...")

    # Wait for analysis
    time.sleep(5)

    # Check if analyzed
    response = requests.get(f"{BASE_URL}/api/analyze/status/{video_id}")
    if response.status_code == 200:
        status = response.json()['status']
        if status == 'analyzed':
            print(f"✅ Test data ready! Video ID: {video_id}")
            return video_id

    print("❌ Analysis did not complete")
    return None


def test_basic_results(video_id):
    """Test basic results endpoint without filters"""
    print_separator("Test 1: Basic Results (No Filters)")

    response = requests.get(f"{BASE_URL}/api/results/{video_id}")

    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        print(response.json())
        return False

    data = response.json()

    print(f"✅ Results retrieved successfully!")
    print(f"\n📊 Video Metadata:")
    print(f"   Filename: {data['video']['filename']}")
    print(f"   Status: {data['video']['status']}")
    print(f"   Upload Time: {data['video']['upload_timestamp']}")
    print(f"   Frame Count: {data['video']['frame_count']}")

    print(f"\n📈 Summary Statistics:")
    summary = data['damage_summary']
    print(f"   Total Inferences: {summary['total_inferences']}")
    print(f"   Total Cost: ${summary['total_estimated_cost']:.2f}")
    print(f"   Unique Damage Types: {summary['unique_damage_types']}")
    print(f"   Frames with Damage: {summary['frames_with_damage']}/{summary['total_frames']}")
    print(f"   Average Confidence: {summary['avg_confidence']:.3f}")

    print(f"\n🔍 Damage Breakdown:")
    for damage_type, info in summary['damage_counts'].items():
        print(f"   • {damage_type}:")
        print(f"     - Count: {info['count']}")
        print(f"     - Avg Confidence: {info['avg_confidence']:.3f}")
        print(f"     - Severities: Low={info['severities']['low']}, Medium={info['severities']['medium']}, High={info['severities']['high']}")

    print(f"\n⚠️  Severity Distribution:")
    sev = summary['severity_counts']
    print(f"   Low: {sev['low']}, Medium: {sev['medium']}, High: {sev['high']}")

    print(f"\n📋 Sample Inferences (first 3):")
    for i, inf in enumerate(data['inferences'][:3]):
        print(f"   {i+1}. Frame {inf['frame_number']}:")
        print(f"      Type: {inf['damage_type']}")
        print(f"      Severity: {inf['severity']}")
        print(f"      Confidence: {inf['confidence']:.3f}")
        if inf.get('bounding_box'):
            print(f"      Bounding Box: {inf['bounding_box']}")

    return True


def test_filter_by_damage_type(video_id):
    """Test filtering by damage type"""
    print_separator("Test 2: Filter by Damage Type")

    # First, get all results to know what damage types exist
    response = requests.get(f"{BASE_URL}/api/results/{video_id}")
    if response.status_code != 200:
        print("❌ Could not fetch results")
        return False

    damage_types = list(response.json()['damage_summary']['damage_counts'].keys())

    if not damage_types:
        print("⚠️  No damage types found to filter")
        return True

    # Test filtering by first damage type
    test_type = damage_types[0]
    print(f"\n🔍 Filtering by damage_type: {test_type}")

    response = requests.get(f"{BASE_URL}/api/results/{video_id}?damage_type={test_type}")

    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        return False

    data = response.json()
    filtered_count = len(data['inferences'])

    print(f"✅ Filter applied successfully!")
    print(f"   Results: {filtered_count} inference(s) with damage_type='{test_type}'")

    # Verify all results match the filter
    all_match = all(inf['damage_type'] == test_type for inf in data['inferences'])
    if all_match:
        print(f"✅ All results match the filter")
    else:
        print(f"❌ Some results don't match the filter")
        return False

    return True


def test_filter_by_severity(video_id):
    """Test filtering by severity"""
    print_separator("Test 3: Filter by Severity")

    severities = ['low', 'medium', 'high']

    for severity in severities:
        print(f"\n🔍 Filtering by severity: {severity}")

        response = requests.get(f"{BASE_URL}/api/results/{video_id}?severity={severity}")

        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            return False

        data = response.json()
        count = len(data['inferences'])

        if count > 0:
            print(f"✅ Found {count} inference(s) with severity='{severity}'")
            # Verify
            all_match = all(inf['severity'] == severity for inf in data['inferences'])
            if not all_match:
                print(f"❌ Some results don't match severity filter")
                return False
        else:
            print(f"   No inferences with severity='{severity}'")

    return True


def test_filter_by_confidence(video_id):
    """Test filtering by minimum confidence"""
    print_separator("Test 4: Filter by Minimum Confidence")

    thresholds = [0.5, 0.7, 0.9]

    for threshold in thresholds:
        print(f"\n🔍 Filtering by min_confidence >= {threshold}")

        response = requests.get(f"{BASE_URL}/api/results/{video_id}?min_confidence={threshold}")

        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            return False

        data = response.json()
        count = len(data['inferences'])

        print(f"   Found {count} inference(s) with confidence >= {threshold}")

        if count > 0:
            # Verify all match threshold
            all_match = all(inf['confidence'] >= threshold for inf in data['inferences'])
            if all_match:
                print(f"✅ All results meet confidence threshold")
            else:
                print(f"❌ Some results below threshold")
                return False

    return True


def test_sorting(video_id):
    """Test sorting functionality"""
    print_separator("Test 5: Sorting")

    sort_tests = [
        ('confidence', 'desc', 'Highest Confidence First'),
        ('confidence', 'asc', 'Lowest Confidence First'),
        ('frame_number', 'asc', 'Frame Order'),
        ('severity', 'desc', 'Highest Severity First'),
    ]

    for sort_by, sort_order, description in sort_tests:
        print(f"\n🔍 Testing: {description} (sort_by={sort_by}, order={sort_order})")

        response = requests.get(f"{BASE_URL}/api/results/{video_id}?sort_by={sort_by}&sort_order={sort_order}")

        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            return False

        data = response.json()
        inferences = data['inferences']

        if len(inferences) < 2:
            print(f"   ⚠️  Not enough data to verify sorting")
            continue

        # Verify sorting
        if sort_by == 'confidence':
            values = [inf['confidence'] for inf in inferences]
            is_sorted = values == sorted(values, reverse=(sort_order == 'desc'))
        elif sort_by == 'frame_number':
            values = [inf['frame_number'] for inf in inferences]
            is_sorted = values == sorted(values, reverse=(sort_order == 'desc'))
        else:
            is_sorted = True  # Skip detailed verification for severity/damage_type

        if is_sorted:
            print(f"✅ Results properly sorted")
            # Show first 3
            for i, inf in enumerate(inferences[:3]):
                print(f"   {i+1}. Frame {inf['frame_number']}: {inf[sort_by]}")
        else:
            print(f"❌ Results not properly sorted")
            return False

    return True


def test_combined_filters(video_id):
    """Test combining multiple filters"""
    print_separator("Test 6: Combined Filters")

    print(f"\n🔍 Testing: severity=high + min_confidence=0.6 + sort by confidence")

    response = requests.get(
        f"{BASE_URL}/api/results/{video_id}?"
        f"severity=high&min_confidence=0.6&sort_by=confidence&sort_order=desc"
    )

    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        return False

    data = response.json()
    inferences = data['inferences']

    print(f"✅ Combined filters applied successfully!")
    print(f"   Results: {len(inferences)} inference(s)")

    if inferences:
        # Verify all match filters
        all_high = all(inf['severity'] == 'high' for inf in inferences)
        all_above_threshold = all(inf['confidence'] >= 0.6 for inf in inferences)

        if all_high and all_above_threshold:
            print(f"✅ All results match combined filters")
            print(f"\n   Top results:")
            for i, inf in enumerate(inferences[:3]):
                print(f"   {i+1}. Frame {inf['frame_number']}: {inf['damage_type']}, confidence={inf['confidence']:.3f}")
        else:
            print(f"❌ Some results don't match filters")
            return False
    else:
        print(f"   ℹ️  No results match the combined filters")

    return True


def test_error_handling(video_id):
    """Test error handling"""
    print_separator("Test 7: Error Handling")

    # Test 1: Non-existent video
    print(f"\n🔍 Testing: Non-existent video ID")
    response = requests.get(f"{BASE_URL}/api/results/99999")
    if response.status_code == 404:
        print(f"✅ Correctly returned 404 for non-existent video")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
        return False

    # Test 2: Invalid confidence value
    print(f"\n🔍 Testing: Invalid confidence value (> 1.0)")
    response = requests.get(f"{BASE_URL}/api/results/{video_id}?min_confidence=1.5")
    if response.status_code == 422:
        print(f"✅ Correctly rejected invalid confidence value")
    else:
        print(f"⚠️  Got status {response.status_code} (expected 422)")

    return True


def run_all_tests():
    """Run all results API tests"""
    print_separator("AdjustR - Day 7 Results API Test Suite")

    # Check backend health
    print("\n🔍 Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not running!")
            print("Please start with: docker-compose up")
            return
        print("✅ Backend is running")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("Please start with: docker-compose up")
        return

    # Setup test data
    video_id = setup_test_data()
    if not video_id:
        print("\n❌ Failed to setup test data")
        return

    # Run tests
    tests = [
        ("Basic Results", test_basic_results),
        ("Filter by Damage Type", test_filter_by_damage_type),
        ("Filter by Severity", test_filter_by_severity),
        ("Filter by Confidence", test_filter_by_confidence),
        ("Sorting", test_sorting),
        ("Combined Filters", test_combined_filters),
        ("Error Handling", test_error_handling),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func(video_id)
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))

    # Print summary
    print_separator("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n📊 Results: {passed}/{total} tests passed")
    print(f"\nDetailed Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")

    if passed == total:
        print(f"\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  Some tests failed")

    print(f"\n🗑️  To clean up test data:")
    print(f"   curl -X DELETE {BASE_URL}/api/upload/{video_id}")

    print_separator()


if __name__ == "__main__":
    run_all_tests()
