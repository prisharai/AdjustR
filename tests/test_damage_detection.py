"""
Test script for damage detection
Tests YOLOv8 integration and damage detection
"""
import sys
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw
import tempfile

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.damage_detector import DamageDetector, get_damage_detector
from ml.damage_mapping import get_all_damage_types, DAMAGE_COST_ESTIMATES


def create_test_image(filename="test_damage.jpg", image_type="simple"):
    """
    Create test image for damage detection

    Args:
        filename: Output filename
        image_type: Type of test image to create

    Returns:
        Path to created image
    """
    print(f"\n📷 Creating test image: {filename}")

    if image_type == "simple":
        # Create simple colored image
        img = np.zeros((480, 640, 3), dtype=np.uint8)

        # Add some shapes to simulate damage
        # Red rectangle (potential damage area)
        cv2.rectangle(img, (100, 100), (300, 200), (0, 0, 255), -1)

        # Green circle
        cv2.circle(img, (450, 300), 50, (0, 255, 0), -1)

        # Add text
        cv2.putText(
            img,
            "Test Damage Image",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.imwrite(filename, img)

    elif image_type == "complex":
        # Create more complex scene
        img = Image.new('RGB', (800, 600), color=(200, 200, 200))
        draw = ImageDraw.Draw(img)

        # Draw "damaged" areas
        draw.rectangle([50, 50, 250, 150], fill=(139, 69, 19), outline=(0, 0, 0))
        draw.ellipse([400, 100, 600, 300], fill=(100, 100, 100), outline=(0, 0, 0))
        draw.rectangle([100, 400, 300, 550], fill=(0, 0, 139), outline=(0, 0, 0))

        img.save(filename)

    elif image_type == "realistic":
        # Create a more realistic looking damage scene
        img = np.ones((600, 800, 3), dtype=np.uint8) * 200

        # Simulate wall
        cv2.rectangle(img, (0, 0), (800, 600), (230, 230, 230), -1)

        # Add "crack" pattern
        for i in range(5):
            pt1 = (200 + i * 30, 100 + i * 20)
            pt2 = (250 + i * 30, 150 + i * 20)
            cv2.line(img, pt1, pt2, (50, 50, 50), 3)

        # Add "water stain"
        cv2.circle(img, (600, 300), 80, (180, 180, 200), -1)
        cv2.circle(img, (600, 300), 60, (160, 160, 180), -1)

        cv2.imwrite(filename, img)

    print(f"✓ Created test image: {filename}")
    return filename


def test_detector_initialization():
    """Test 1: Initialize damage detector"""
    print("\n" + "=" * 60)
    print("Test 1: Damage Detector Initialization")
    print("=" * 60)

    try:
        print("\n📦 Initializing YOLOv8 detector...")
        print("   (First run will download the model)")

        detector = DamageDetector(model_path="yolov8n.pt")

        print("✓ Detector initialized successfully")
        print(f"  Model: {detector.model_path}")
        print(f"  Model loaded: {detector.model is not None}")

        return detector

    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_simple_detection(detector):
    """Test 2: Detect damage in simple image"""
    print("\n" + "=" * 60)
    print("Test 2: Simple Damage Detection")
    print("=" * 60)

    # Create test image
    test_image = create_test_image("test_simple.jpg", "simple")

    try:
        print("\n🔍 Running detection...")

        detections = detector.detect_damage(
            image_path=test_image,
            confidence_threshold=0.25
        )

        print(f"\n✓ Detection complete")
        print(f"  Total detections: {len(detections)}")

        if detections:
            print("\n  Detected damage:")
            for i, det in enumerate(detections):
                print(f"    {i+1}. {det['damage_type']}")
                print(f"       Severity: {det['severity']}")
                print(f"       Confidence: {det['confidence']:.3f}")
                print(f"       Estimated cost: ${det['estimated_cost']:.2f}")
        else:
            print("  ℹ️  No damage detected (this is expected for simple test images)")
            print("      YOLOv8 is trained on real objects, not synthetic shapes")

        # Create visualization
        if detections:
            output_path = "test_simple_annotated.jpg"
            detector.visualize_detections(test_image, detections, output_path)
            print(f"\n  📸 Annotated image saved: {output_path}")

        # Get summary
        summary = detector.get_damage_summary(detections)
        print(f"\n  Summary:")
        print(f"    Total estimated cost: ${summary['total_estimated_cost']:.2f}")
        print(f"    Severity breakdown: {summary['severity_counts']}")

        return True

    except Exception as e:
        print(f"❌ Detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if os.path.exists(test_image):
            os.remove(test_image)


def test_with_real_image(detector):
    """Test 3: Test with user-provided image"""
    print("\n" + "=" * 60)
    print("Test 3: Real Image Detection")
    print("=" * 60)

    # Check if user provided an image
    if len(sys.argv) > 1:
        image_path = sys.argv[1]

        if not os.path.exists(image_path):
            print(f"⚠️  Image not found: {image_path}")
            return False

        try:
            print(f"\n🔍 Detecting damage in: {image_path}")

            detections = detector.detect_damage(
                image_path=image_path,
                confidence_threshold=0.25
            )

            print(f"\n✓ Detection complete")
            print(f"  Total detections: {len(detections)}")

            if detections:
                print("\n  Detected damage:")
                for i, det in enumerate(detections):
                    print(f"\n    {i+1}. {det['damage_type']} ({det['yolo_class']})")
                    print(f"       Severity: {det['severity']}")
                    print(f"       Confidence: {det['confidence']:.3f}")
                    print(f"       Estimated cost: ${det['estimated_cost']:.2f}")
                    print(f"       Bounding box: ({det['bounding_box']['x1']:.0f}, "
                          f"{det['bounding_box']['y1']:.0f}) → "
                          f"({det['bounding_box']['x2']:.0f}, {det['bounding_box']['y2']:.0f})")

                # Create visualization
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_path = f"{base_name}_annotated.jpg"
                detector.visualize_detections(image_path, detections, output_path)
                print(f"\n  📸 Annotated image saved: {output_path}")

                # Summary
                summary = detector.get_damage_summary(detections)
                print(f"\n  📊 Summary:")
                print(f"    Total estimated cost: ${summary['total_estimated_cost']:.2f}")
                print(f"    Average confidence: {summary['average_confidence']:.3f}")
                print(f"    Severity breakdown:")
                print(f"      Low: {summary['severity_counts']['low']}")
                print(f"      Medium: {summary['severity_counts']['medium']}")
                print(f"      High: {summary['severity_counts']['high']}")

                print(f"\n    Damage types found:")
                for dtype, info in summary['damage_types'].items():
                    print(f"      {dtype}: {info['count']} instances, "
                          f"${info['total_cost']:.2f} total")

            else:
                print("  ℹ️  No relevant damage detected in this image")
                print("      (YOLOv8 detects known objects; custom training needed for specific damage types)")

            return True

        except Exception as e:
            print(f"❌ Detection failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    else:
        print("\nℹ️  To test with your own image:")
        print("   python test_damage_detection.py <image_path>")
        return True


def test_damage_types():
    """Test 4: Show available damage types"""
    print("\n" + "=" * 60)
    print("Test 4: Available Damage Types")
    print("=" * 60)

    damage_types = get_all_damage_types()

    print(f"\n📋 {len(damage_types)} damage types configured:")
    print()

    for dtype in sorted(damage_types):
        cost = DAMAGE_COST_ESTIMATES.get(dtype, 0)
        print(f"  • {dtype:.<30} ${cost:>6,.2f}")


def test_batch_detection(detector):
    """Test 5: Batch processing"""
    print("\n" + "=" * 60)
    print("Test 5: Batch Detection")
    print("=" * 60)

    # Create multiple test images
    print("\n📷 Creating multiple test images...")

    test_images = []
    for i in range(3):
        img_name = f"test_batch_{i}.jpg"
        create_test_image(img_name, "simple")
        test_images.append(img_name)

    try:
        print(f"\n🔍 Running batch detection on {len(test_images)} images...")

        results = detector.detect_batch(test_images, confidence_threshold=0.25)

        print(f"\n✓ Batch detection complete")

        total_detections = sum(len(dets) for dets in results.values())
        print(f"  Total detections across all images: {total_detections}")

        for img_path, detections in results.items():
            print(f"\n  {os.path.basename(img_path)}: {len(detections)} detections")

        return True

    except Exception as e:
        print(f"❌ Batch detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        for img in test_images:
            if os.path.exists(img):
                os.remove(img)


def run_all_tests():
    """Run all damage detection tests"""
    print("=" * 60)
    print("YOLOv8 Damage Detection - Test Suite")
    print("=" * 60)

    # Test 1: Initialization
    detector = test_detector_initialization()
    if detector is None:
        print("\n❌ Cannot proceed without detector")
        return

    # Test 2: Simple detection
    test_simple_detection(detector)

    # Test 3: Real image (if provided)
    test_with_real_image(detector)

    # Test 4: Damage types
    test_damage_types()

    # Test 5: Batch detection
    test_batch_detection(detector)

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

    print("\n💡 Notes:")
    print("  • YOLOv8 is pretrained on COCO dataset (everyday objects)")
    print("  • For accurate property damage detection, fine-tuning is recommended")
    print("  • Current implementation uses heuristics to map objects → damage types")
    print("  • For production: train custom model on damage images")
    print()
    print("  To test with your own image:")
    print("    python test_damage_detection.py path/to/your/image.jpg")


if __name__ == "__main__":
    run_all_tests()
