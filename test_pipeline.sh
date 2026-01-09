#!/bin/bash

# Test script for complete analysis pipeline

BASE_URL="http://localhost:8000"

echo "============================================"
echo "Testing Complete Analysis Pipeline"
echo "============================================"

# Check backend health
echo ""
echo "1. Checking backend..."
curl -s $BASE_URL/health | python3 -m json.tool > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Backend is running"
else
    echo "✗ Backend is not running"
    echo "  Please start with: docker-compose up"
    exit 1
fi

# Create test image
echo ""
echo "2. Creating test image..."
python3 -c "from PIL import Image; img = Image.new('RGB', (800, 600), (200, 200, 200)); img.save('/tmp/test_pipeline.jpg')"
echo "✓ Test image created"

# Upload
echo ""
echo "3. Uploading image..."
RESPONSE=$(curl -s -X POST $BASE_URL/api/upload \
  -F "file=@/tmp/test_pipeline.jpg")

VIDEO_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('video_id', ''))" 2>/dev/null)

if [ ! -z "$VIDEO_ID" ]; then
    echo "✓ Upload successful! Video ID: $VIDEO_ID"
else
    echo "✗ Upload failed"
    exit 1
fi

# Wait for processing
echo ""
echo "4. Waiting for frame extraction..."
sleep 3

STATUS=$(curl -s $BASE_URL/api/upload/status/$VIDEO_ID | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)
echo "   Status: $STATUS"

# Trigger analysis
echo ""
echo "5. Triggering damage analysis..."
curl -s -X POST $BASE_URL/api/analyze/$VIDEO_ID | python3 -m json.tool

# Wait for analysis
echo ""
echo "6. Waiting for analysis..."
sleep 5

# Get results
echo ""
echo "7. Fetching results..."
curl -s $BASE_URL/api/analyze/status/$VIDEO_ID | python3 -m json.tool

# Cleanup
echo ""
echo "8. Cleaning up..."
rm -f /tmp/test_pipeline.jpg
echo "✓ Test image removed"

echo ""
echo "============================================"
echo "Pipeline test complete!"
echo "============================================"

echo ""
echo "To delete test data:"
echo "  curl -X DELETE $BASE_URL/api/upload/$VIDEO_ID"
