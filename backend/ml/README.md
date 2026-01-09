# ML Module - Damage Detection

This module contains the machine learning components for AdjustR's damage detection system.

## Components

### 1. Video Processor (`video_processor.py`)
Extracts keyframes from uploaded videos using OpenCV.

**Features**:
- Configurable keyframe interval (default: 2 seconds)
- Automatic FPS detection
- JPEG compression for frames
- Image processing support

**Usage**:
```python
from ml.video_processor import VideoProcessor

processor = VideoProcessor(keyframe_interval=2.0)
frames, duration, count = processor.extract_keyframes(
    video_path="video.mp4",
    output_dir="/tmp/frames"
)
```

---

### 2. Damage Detector (`damage_detector.py`)
Detects property damage using YOLOv8 object detection.

**Features**:
- YOLOv8 pretrained model
- Damage type mapping
- Severity classification
- Cost estimation
- Batch processing
- Visualization

**Usage**:
```python
from ml.damage_detector import get_damage_detector

detector = get_damage_detector()
detections = detector.detect_damage(
    image_path="frame.jpg",
    confidence_threshold=0.25
)

# Get summary
summary = detector.get_damage_summary(detections)
print(f"Total cost: ${summary['total_estimated_cost']}")

# Visualize
detector.visualize_detections("frame.jpg", detections, "output.jpg")
```

---

### 3. Damage Mapping (`damage_mapping.py`)
Maps YOLOv8 detections to property damage types.

**Features**:
- YOLO class → damage type mapping
- Severity calculation (low/medium/high)
- Cost estimation per damage type
- Configurable cost tables

**Damage Types**:
- Ceiling Crack ($1,300)
- Wall Damage ($800)
- Water Damage ($1,800)
- Mold ($2,400)
- Fire Damage ($5,000)
- Plumbing Damage ($1,500)
- Broken Window ($500)
- Roof Damage ($3,500)
- And more...

**Severity Levels**:
- **Low**: confidence < 0.5, cost × 0.7
- **Medium**: confidence 0.5-0.75, cost × 1.0
- **High**: confidence > 0.75, cost × 1.5

---

## Detection Pipeline (Day 6)

The complete pipeline (to be implemented):

```
1. Upload video/image
   ↓
2. Extract keyframes (video_processor.py)
   ↓
3. For each frame:
   a. Run YOLOv8 inference (damage_detector.py)
   b. Map detections to damage types (damage_mapping.py)
   c. Calculate severity and cost
   d. Store in database (Inference model)
   ↓
4. Generate summary report
   ↓
5. Return results to frontend
```

---

## Model Information

### YOLOv8 Variants

| Model | Size | Speed | mAP |
|-------|------|-------|-----|
| yolov8n.pt | ~6MB | Fastest | Lowest |
| yolov8s.pt | ~22MB | Fast | Low |
| yolov8m.pt | ~50MB | Medium | Medium |
| yolov8l.pt | ~87MB | Slow | High |
| yolov8x.pt | ~130MB | Slowest | Highest |

**Current**: Using `yolov8n.pt` (nano) for speed
**Production**: Consider `yolov8m.pt` or `yolov8l.pt` for better accuracy

### COCO Dataset

YOLOv8 is pretrained on the COCO dataset (80 classes of everyday objects).

**Relevant classes for damage detection**:
- Toilet, sink → Plumbing damage
- Oven, refrigerator → Appliance damage
- Window-related objects → Window damage

**Limitations**:
- Not trained specifically on property damage
- May miss subtle damage (cracks, water stains, etc.)
- Best results on clear, well-defined objects

**Future Improvement**:
- Fine-tune YOLOv8 on custom property damage dataset
- Train custom model with labels like "crack", "water_stain", "mold", etc.
- Collect and label real insurance claim images

---

## Testing

Run the test suite:

```bash
# From project root
./test_detection.sh

# Or directly
cd backend
python test_damage_detection.py

# Test with your own image
python test_damage_detection.py /path/to/image.jpg
```

**Test Coverage**:
1. Detector initialization
2. Simple image detection
3. Real image detection (if provided)
4. Damage types listing
5. Batch processing

---

## Configuration

### Adjusting Confidence Threshold

Lower threshold = more detections (more false positives)
Higher threshold = fewer detections (more false negatives)

```python
# More sensitive (may detect non-damage)
detections = detector.detect_damage(image, confidence_threshold=0.15)

# More strict (may miss some damage)
detections = detector.detect_damage(image, confidence_threshold=0.50)
```

**Recommended**: 0.25 for MVP

### Custom Cost Estimates

Edit `damage_mapping.py`:

```python
DAMAGE_COST_ESTIMATES = {
    'Ceiling Crack': 1500,  # Change from 1300
    'Custom Damage Type': 2000,  # Add new type
}
```

### Adding New Damage Types

1. Add to `DAMAGE_TYPE_MAPPING` in `damage_mapping.py`
2. Add cost estimate to `DAMAGE_COST_ESTIMATES`
3. Update detection logic if needed

---

## Performance

### Inference Speed

| Model | Resolution | FPS (CPU) | FPS (GPU) |
|-------|-----------|-----------|-----------|
| yolov8n | 640x640 | ~30 | ~200 |
| yolov8s | 640x640 | ~20 | ~150 |
| yolov8m | 640x640 | ~10 | ~100 |

**Note**: Actual speed depends on hardware

### Memory Usage

| Model | RAM | VRAM (GPU) |
|-------|-----|------------|
| yolov8n | ~500MB | ~1GB |
| yolov8s | ~800MB | ~1.5GB |
| yolov8m | ~1.5GB | ~3GB |

---

## Troubleshooting

### Model Download Issues

```python
# Manual download
from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # Downloads automatically
```

### CUDA/GPU Issues

```python
# Force CPU
import torch
torch.cuda.is_available = lambda: False
```

### Low Detection Quality

1. Try larger model (yolov8s or yolov8m)
2. Lower confidence threshold
3. Ensure good image quality
4. Consider fine-tuning on custom data

---

## Next Steps

### Day 6: Integration
- Connect detector to upload pipeline
- Process all extracted frames
- Store inferences in database
- Calculate aggregate costs

### Future Enhancements
- Custom model training
- Real-time processing
- Multi-model ensemble
- Damage severity ML model
- Image quality assessment
