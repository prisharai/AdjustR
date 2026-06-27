"""
Property damage detector using NVIDIA LocateAnything-3B.
Open-set vision-language grounding — detect arbitrary damage types via natural language.
"""
from transformers import pipeline
from PIL import Image
import re
import logging
import os
from typing import List, Dict, Optional
from src.ml.damage_mapping import (
    DAMAGE_COST_ESTIMATES,
    calculate_severity,
    get_damage_cost,
)

logger = logging.getLogger(__name__)

MODEL_ID = "nvidia/LocateAnything-3B"

DAMAGE_QUERIES = [
    "roof damage",
    "broken window",
    "water damage stain",
    "mold",
    "ceiling crack",
    "wall hole",
    "fire damage",
    "smoke damage",
    "floor damage",
    "structural damage",
]

# Map query strings → canonical damage type labels
QUERY_TO_DAMAGE = {
    "roof damage": "Roof Damage",
    "broken window": "Broken Window",
    "water damage stain": "Water Damage",
    "mold": "Mold",
    "ceiling crack": "Ceiling Crack",
    "wall hole": "Wall Damage",
    "fire damage": "Fire Damage",
    "smoke damage": "Smoke Damage",
    "floor damage": "Floor Damage",
    "structural damage": "Structural Damage",
}


def _parse_boxes(text: str) -> List[List[float]]:
    """Extract normalized [x1, y1, x2, y2] boxes from model output tokens."""
    pattern = r"<box>\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*</box>"
    matches = re.findall(pattern, text)
    return [[float(v) for v in m] for m in matches]


class DamageDetector:
    def __init__(self, model_id: str = MODEL_ID, device: str = "cpu"):
        self.model_id = model_id
        self.device = device
        self._pipe = None
        self._load_model()

    def _load_model(self):
        logger.info(f"Loading {self.model_id}")
        self._pipe = pipeline(
            "image-text-to-text",
            model=self.model_id,
            trust_remote_code=True,
            device=self.device,
        )
        logger.info("Model loaded")

    def detect_damage(
        self,
        image_path: str,
        queries: Optional[List[str]] = None,
        confidence_threshold: float = 0.25,
    ) -> List[Dict]:
        if not os.path.exists(image_path):
            raise FileNotFoundError(image_path)

        img = Image.open(image_path).convert("RGB")
        w, h = img.size
        img_area = w * h

        active_queries = queries or DAMAGE_QUERIES
        detections = []

        for query in active_queries:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": img},
                        {"type": "text", "text": f"Locate all instances of: {query}"},
                    ],
                }
            ]

            try:
                output = self._pipe(text=messages, max_new_tokens=256)
                response_text = output[0]["generated_text"][-1]["content"]
            except Exception as e:
                logger.warning(f"Inference failed for query '{query}': {e}")
                continue

            boxes = _parse_boxes(response_text)
            if not boxes:
                continue

            damage_type = QUERY_TO_DAMAGE.get(query, "General Damage")

            for box in boxes:
                x1, y1, x2, y2 = box
                # Coordinates are normalized 0–1000 integers per LocateAnything spec
                x1_px, y1_px = (x1 / 1000) * w, (y1 / 1000) * h
                x2_px, y2_px = (x2 / 1000) * w, (y2 / 1000) * h
                bbox_area = (x2_px - x1_px) * (y2_px - y1_px)
                normalized_area = bbox_area / img_area if img_area > 0 else 0.0

                # LocateAnything doesn't return per-box confidence; use 0.7 as default
                confidence = 0.7
                if confidence < confidence_threshold:
                    continue

                severity = calculate_severity(confidence, normalized_area)
                estimated_cost = get_damage_cost(damage_type, severity)

                detections.append({
                    "damage_type": damage_type,
                    "severity": severity,
                    "confidence": confidence,
                    "bounding_box": {
                        "x1": x1_px,
                        "y1": y1_px,
                        "x2": x2_px,
                        "y2": y2_px,
                        "width": x2_px - x1_px,
                        "height": y2_px - y1_px,
                        "area_normalized": normalized_area,
                    },
                    "query": query,
                    "estimated_cost": estimated_cost,
                })

        logger.info(f"Found {len(detections)} damage detections in {image_path}")
        return detections

    def detect_batch(
        self,
        image_paths: List[str],
        confidence_threshold: float = 0.25,
    ) -> Dict[str, List[Dict]]:
        return {
            path: self._safe_detect(path, confidence_threshold)
            for path in image_paths
        }

    def _safe_detect(self, image_path: str, confidence_threshold: float) -> List[Dict]:
        try:
            return self.detect_damage(image_path, confidence_threshold=confidence_threshold)
        except Exception as e:
            logger.error(f"Failed to process {image_path}: {e}")
            return []

    def get_damage_summary(self, detections: List[Dict]) -> Dict:
        if not detections:
            return {
                "total_detections": 0,
                "total_estimated_cost": 0.0,
                "damage_types": {},
                "severity_counts": {"low": 0, "medium": 0, "high": 0},
                "average_confidence": 0.0,
            }

        damage_types: Dict[str, Dict] = {}
        for det in detections:
            dtype = det["damage_type"]
            if dtype not in damage_types:
                damage_types[dtype] = {"count": 0, "total_cost": 0.0, "avg_confidence": 0.0}
            damage_types[dtype]["count"] += 1
            damage_types[dtype]["total_cost"] += det["estimated_cost"]

        for dtype in damage_types:
            subset = [d for d in detections if d["damage_type"] == dtype]
            damage_types[dtype]["avg_confidence"] = sum(d["confidence"] for d in subset) / len(subset)

        return {
            "total_detections": len(detections),
            "total_estimated_cost": sum(d["estimated_cost"] for d in detections),
            "damage_types": damage_types,
            "severity_counts": {
                sev: sum(1 for d in detections if d["severity"] == sev)
                for sev in ("low", "medium", "high")
            },
            "average_confidence": sum(d["confidence"] for d in detections) / len(detections),
        }


_detector_instance: Optional[DamageDetector] = None


def get_damage_detector(model_id: str = MODEL_ID) -> DamageDetector:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = DamageDetector(model_id)
    return _detector_instance
