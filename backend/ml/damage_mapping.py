"""
Damage type mapping and classification
Maps YOLO object detections to property damage types
"""
from typing import Dict, Optional, Tuple


# YOLO COCO class names (YOLOv8 pretrained on COCO dataset)
# We'll map relevant classes to damage types
YOLO_COCO_CLASSES = {
    # Objects that might indicate damage
    'person': None,  # Ignore
    'car': None,  # Ignore
    'chair': None,  # Ignore
    'couch': None,  # Ignore
    'bed': None,  # Ignore
    'dining table': None,  # Ignore
    'toilet': 'Plumbing Damage',
    'tv': None,  # Ignore
    'laptop': None,  # Ignore
    'mouse': None,  # Ignore
    'keyboard': None,  # Ignore
    'cell phone': None,  # Ignore
    'microwave': None,  # Ignore
    'oven': 'Appliance Damage',
    'toaster': None,  # Ignore
    'sink': 'Plumbing Damage',
    'refrigerator': 'Appliance Damage',
    'book': None,  # Ignore
    'clock': None,  # Ignore
    'vase': None,  # Ignore
    'scissors': None,  # Ignore
    'teddy bear': None,  # Ignore
    'hair drier': None,  # Ignore
    'toothbrush': None,  # Ignore
}

# Damage type mapping based on visual patterns
# For MVP, we'll use a heuristic approach:
# - High confidence detections of certain objects may indicate issues
# - Unusual patterns or multiple detections can suggest damage
# - This will be enhanced with a custom-trained model later

DAMAGE_TYPE_MAPPING = {
    # Structural damage indicators
    'crack': 'Ceiling Crack',
    'hole': 'Wall Damage',
    'broken': 'Structural Damage',
    'damaged': 'General Damage',

    # Water damage indicators
    'water': 'Water Damage',
    'stain': 'Water Damage',
    'leak': 'Water Damage',
    'wet': 'Water Damage',
    'mold': 'Mold',
    'mildew': 'Mold',

    # Fire damage indicators
    'burn': 'Fire Damage',
    'smoke': 'Smoke Damage',
    'soot': 'Smoke Damage',
    'char': 'Fire Damage',

    # Appliance/plumbing
    'toilet': 'Plumbing Damage',
    'sink': 'Plumbing Damage',
    'refrigerator': 'Appliance Damage',
    'oven': 'Appliance Damage',

    # Floor damage
    'floor': 'Floor Damage',
    'carpet': 'Floor Damage',
    'tile': 'Floor Damage',

    # Window/glass damage
    'window': 'Broken Window',
    'glass': 'Broken Window',

    # Roof damage
    'roof': 'Roof Damage',
    'shingle': 'Roof Damage',

    # Default catch-all
    'unknown': 'General Damage'
}

# Cost estimates per damage type (in USD)
# These are rough estimates for MVP
DAMAGE_COST_ESTIMATES = {
    'Ceiling Crack': 1300,
    'Wall Damage': 800,
    'Structural Damage': 3000,
    'General Damage': 1000,
    'Water Damage': 1800,
    'Mold': 2400,
    'Fire Damage': 5000,
    'Smoke Damage': 2000,
    'Plumbing Damage': 1500,
    'Appliance Damage': 1200,
    'Floor Damage': 2000,
    'Broken Window': 500,
    'Roof Damage': 3500,
    'Damaged Drywall': 800,
}

# Severity levels based on confidence and bounding box size
SEVERITY_THRESHOLDS = {
    'low': (0.0, 0.5),      # confidence < 0.5
    'medium': (0.5, 0.75),  # confidence 0.5 - 0.75
    'high': (0.75, 1.0)     # confidence > 0.75
}

# Severity multipliers for cost estimation
SEVERITY_MULTIPLIERS = {
    'low': 0.7,
    'medium': 1.0,
    'high': 1.5
}


def map_detection_to_damage(
    class_name: str,
    confidence: float,
    bbox_area: float = 0.0
) -> Tuple[Optional[str], str]:
    """
    Map YOLO detection to damage type and severity

    Args:
        class_name: YOLO class name
        confidence: Detection confidence score (0-1)
        bbox_area: Normalized bounding box area (0-1)

    Returns:
        Tuple of (damage_type, severity)
    """
    # Check if we should ignore this detection
    if class_name in YOLO_COCO_CLASSES:
        damage_type = YOLO_COCO_CLASSES[class_name]
        if damage_type is None:
            return None, 'none'
    else:
        # Try to find matching damage type
        damage_type = None
        class_lower = class_name.lower()

        for keyword, damage in DAMAGE_TYPE_MAPPING.items():
            if keyword in class_lower:
                damage_type = damage
                break

        if damage_type is None:
            damage_type = 'General Damage'

    # Calculate severity
    severity = calculate_severity(confidence, bbox_area)

    return damage_type, severity


def calculate_severity(confidence: float, bbox_area: float = 0.0) -> str:
    """
    Calculate damage severity based on confidence and size

    Args:
        confidence: Detection confidence (0-1)
        bbox_area: Normalized bounding box area (0-1)

    Returns:
        Severity level: 'low', 'medium', or 'high'
    """
    # Primary factor: confidence
    if confidence < 0.5:
        base_severity = 'low'
    elif confidence < 0.75:
        base_severity = 'medium'
    else:
        base_severity = 'high'

    # Secondary factor: size (if large area, increase severity)
    if bbox_area > 0.3:  # Large damage (>30% of frame)
        if base_severity == 'low':
            base_severity = 'medium'
        elif base_severity == 'medium':
            base_severity = 'high'

    return base_severity


def get_damage_cost(damage_type: str, severity: str) -> float:
    """
    Get estimated cost for damage type and severity

    Args:
        damage_type: Type of damage
        severity: Severity level

    Returns:
        Estimated cost in USD
    """
    base_cost = DAMAGE_COST_ESTIMATES.get(damage_type, 1000)
    multiplier = SEVERITY_MULTIPLIERS.get(severity, 1.0)

    return base_cost * multiplier


def get_all_damage_types() -> list:
    """Get list of all possible damage types"""
    return list(set(DAMAGE_COST_ESTIMATES.keys()))


def is_damage_detection_relevant(class_name: str) -> bool:
    """
    Check if a YOLO detection is relevant for damage assessment

    Args:
        class_name: YOLO class name

    Returns:
        True if detection should be processed
    """
    # Check if explicitly mapped
    if class_name in YOLO_COCO_CLASSES:
        return YOLO_COCO_CLASSES[class_name] is not None

    # Check if matches any damage keyword
    class_lower = class_name.lower()
    for keyword in DAMAGE_TYPE_MAPPING.keys():
        if keyword in class_lower:
            return True

    return False
