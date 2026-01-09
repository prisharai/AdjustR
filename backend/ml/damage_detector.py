"""
Damage detection using YOLOv8
Detects property damage from images using pretrained object detection
"""
from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
import os
from pathlib import Path
from ml.damage_mapping import (
    map_detection_to_damage,
    get_damage_cost,
    is_damage_detection_relevant
)

logger = logging.getLogger(__name__)


class DamageDetector:
    """
    Damage detector using YOLOv8
    """

    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initialize damage detector

        Args:
            model_path: Path to YOLOv8 model weights
                       'yolov8n.pt' - Nano (fastest, least accurate)
                       'yolov8s.pt' - Small
                       'yolov8m.pt' - Medium
                       'yolov8l.pt' - Large
                       'yolov8x.pt' - Extra large (slowest, most accurate)
        """
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load YOLOv8 model"""
        try:
            logger.info(f"Loading YOLOv8 model: {self.model_path}")

            # YOLO will automatically download the model if not present
            self.model = YOLO(self.model_path)

            logger.info(f"✅ YOLOv8 model loaded successfully")
            logger.info(f"   Model: {self.model_path}")
            logger.info(f"   Task: {self.model.task}")

        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            raise

    def detect_damage(
        self,
        image_path: str,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45
    ) -> List[Dict]:
        """
        Detect damage in an image

        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence for detections
            iou_threshold: IoU threshold for NMS

        Returns:
            List of detection dictionaries
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            logger.debug(f"Running inference on: {image_path}")

            # Run inference
            results = self.model.predict(
                source=image_path,
                conf=confidence_threshold,
                iou=iou_threshold,
                verbose=False
            )

            # Parse results
            detections = self._parse_results(results[0], image_path)

            logger.info(f"Detected {len(detections)} potential damage indicators")

            return detections

        except Exception as e:
            logger.error(f"Error detecting damage: {e}")
            raise

    def _parse_results(self, result, image_path: str) -> List[Dict]:
        """
        Parse YOLO results into damage detections

        Args:
            result: YOLO result object
            image_path: Path to source image

        Returns:
            List of detection dictionaries
        """
        detections = []

        # Get image dimensions
        img = cv2.imread(image_path)
        if img is None:
            logger.warning(f"Could not read image: {image_path}")
            return detections

        img_height, img_width = img.shape[:2]
        img_area = img_width * img_height

        # Process each detection
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            logger.debug("No detections in image")
            return detections

        for box in boxes:
            # Extract detection info
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            bbox = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]

            # Get class name
            class_name = result.names[class_id]

            # Check if detection is relevant for damage assessment
            if not is_damage_detection_relevant(class_name):
                logger.debug(f"Ignoring detection: {class_name}")
                continue

            # Calculate bounding box metrics
            x1, y1, x2, y2 = bbox
            bbox_width = x2 - x1
            bbox_height = y2 - y1
            bbox_area = bbox_width * bbox_height
            normalized_area = bbox_area / img_area

            # Map to damage type
            damage_type, severity = map_detection_to_damage(
                class_name=class_name,
                confidence=confidence,
                bbox_area=normalized_area
            )

            if damage_type is None:
                continue

            # Get cost estimate
            estimated_cost = get_damage_cost(damage_type, severity)

            # Create detection dictionary
            detection = {
                'damage_type': damage_type,
                'severity': severity,
                'confidence': float(confidence),
                'bounding_box': {
                    'x1': float(x1),
                    'y1': float(y1),
                    'x2': float(x2),
                    'y2': float(y2),
                    'width': float(bbox_width),
                    'height': float(bbox_height),
                    'area_normalized': float(normalized_area)
                },
                'yolo_class': class_name,
                'yolo_class_id': class_id,
                'estimated_cost': estimated_cost
            }

            detections.append(detection)
            logger.debug(f"  → {damage_type} ({severity}, {confidence:.2f})")

        return detections

    def detect_batch(
        self,
        image_paths: List[str],
        confidence_threshold: float = 0.25
    ) -> Dict[str, List[Dict]]:
        """
        Detect damage in multiple images

        Args:
            image_paths: List of image paths
            confidence_threshold: Minimum confidence

        Returns:
            Dictionary mapping image_path → detections
        """
        results = {}

        for image_path in image_paths:
            try:
                detections = self.detect_damage(
                    image_path=image_path,
                    confidence_threshold=confidence_threshold
                )
                results[image_path] = detections
            except Exception as e:
                logger.error(f"Failed to process {image_path}: {e}")
                results[image_path] = []

        return results

    def visualize_detections(
        self,
        image_path: str,
        detections: List[Dict],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on image

        Args:
            image_path: Path to source image
            detections: List of detections
            output_path: Optional path to save annotated image

        Returns:
            Annotated image as numpy array
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Could not read image: {image_path}")

        # Draw each detection
        for det in detections:
            bbox = det['bounding_box']
            damage_type = det['damage_type']
            severity = det['severity']
            confidence = det['confidence']

            # Extract coordinates
            x1, y1 = int(bbox['x1']), int(bbox['y1'])
            x2, y2 = int(bbox['x2']), int(bbox['y2'])

            # Choose color based on severity
            color_map = {
                'low': (0, 255, 0),      # Green
                'medium': (0, 165, 255),  # Orange
                'high': (0, 0, 255)       # Red
            }
            color = color_map.get(severity, (255, 255, 255))

            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            # Create label
            label = f"{damage_type} ({severity})"
            conf_label = f"{confidence:.2f}"

            # Draw label background
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(
                img,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                color,
                -1
            )

            # Draw label text
            cv2.putText(
                img,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

        # Save if output path provided
        if output_path:
            cv2.imwrite(output_path, img)
            logger.info(f"Saved annotated image to: {output_path}")

        return img

    def get_damage_summary(self, detections: List[Dict]) -> Dict:
        """
        Create summary of detected damage

        Args:
            detections: List of detections

        Returns:
            Summary dictionary
        """
        if not detections:
            return {
                'total_detections': 0,
                'total_estimated_cost': 0.0,
                'damage_types': {},
                'severity_counts': {'low': 0, 'medium': 0, 'high': 0},
                'average_confidence': 0.0
            }

        # Count damage types
        damage_types = {}
        for det in detections:
            dtype = det['damage_type']
            if dtype not in damage_types:
                damage_types[dtype] = {
                    'count': 0,
                    'total_cost': 0.0,
                    'avg_confidence': 0.0
                }
            damage_types[dtype]['count'] += 1
            damage_types[dtype]['total_cost'] += det['estimated_cost']

        # Calculate averages
        for dtype in damage_types:
            count = damage_types[dtype]['count']
            damage_types[dtype]['avg_confidence'] = sum(
                d['confidence'] for d in detections if d['damage_type'] == dtype
            ) / count

        # Count severities
        severity_counts = {
            'low': sum(1 for d in detections if d['severity'] == 'low'),
            'medium': sum(1 for d in detections if d['severity'] == 'medium'),
            'high': sum(1 for d in detections if d['severity'] == 'high')
        }

        # Total cost
        total_cost = sum(d['estimated_cost'] for d in detections)

        # Average confidence
        avg_confidence = sum(d['confidence'] for d in detections) / len(detections)

        return {
            'total_detections': len(detections),
            'total_estimated_cost': float(total_cost),
            'damage_types': damage_types,
            'severity_counts': severity_counts,
            'average_confidence': float(avg_confidence)
        }


# Singleton instance
_detector_instance = None


def get_damage_detector(model_path: str = "yolov8n.pt") -> DamageDetector:
    """
    Get singleton damage detector instance

    Args:
        model_path: Path to YOLOv8 model

    Returns:
        DamageDetector instance
    """
    global _detector_instance

    if _detector_instance is None:
        _detector_instance = DamageDetector(model_path)

    return _detector_instance
