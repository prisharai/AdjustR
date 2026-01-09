"""
File validation utilities
"""
import os
from typing import Tuple
from app.config import settings


def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """
    Validate file extension

    Args:
        filename: Name of file to validate

    Returns:
        Tuple of (is_valid, message)
    """
    _, ext = os.path.splitext(filename.lower())

    if ext not in settings.allowed_extensions:
        return False, f"File type {ext} not allowed. Allowed: {', '.join(settings.allowed_extensions)}"

    return True, "Valid file extension"


def validate_file_size(file_size: int) -> Tuple[bool, str]:
    """
    Validate file size

    Args:
        file_size: Size of file in bytes

    Returns:
        Tuple of (is_valid, message)
    """
    if file_size > settings.max_file_size:
        max_mb = settings.max_file_size / (1024 * 1024)
        return False, f"File too large. Maximum size: {max_mb}MB"

    if file_size == 0:
        return False, "File is empty"

    return True, "Valid file size"


def is_video_file(filename: str) -> bool:
    """Check if file is a video"""
    _, ext = os.path.splitext(filename.lower())
    return ext in ['.mp4', '.mov', '.avi', '.mkv']


def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    _, ext = os.path.splitext(filename.lower())
    return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
