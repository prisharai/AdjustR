#!/bin/bash

# Test script for YOLOv8 damage detection

echo "============================================"
echo "Testing YOLOv8 Damage Detection"
echo "============================================"

cd backend

echo ""
echo "1. Installing required packages..."
pip install -q ultralytics opencv-python pillow 2>/dev/null || echo "  (packages may already be installed)"

echo ""
echo "2. Running damage detection tests..."
python test_damage_detection.py

echo ""
echo "============================================"
echo "Test completed!"
echo "============================================"

echo ""
echo "📝 Notes:"
echo "  • First run downloads YOLOv8 model (~6MB)"
echo "  • Model is cached for future use"
echo "  • To test with your own image:"
echo "    cd backend && python test_damage_detection.py /path/to/image.jpg"
