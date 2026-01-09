#!/bin/bash

# Test script for upload endpoint using curl

BASE_URL="http://localhost:8000"

echo "============================================"
echo "Testing AdjustR Upload API"
echo "============================================"

# Test 1: Health check
echo ""
echo "1. Testing health check..."
curl -s $BASE_URL/health | python3 -m json.tool

# Test 2: Create a test image
echo ""
echo "2. Creating test image..."
# Create a simple 1x1 pixel PNG
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > /tmp/test.png
echo "✓ Test image created: /tmp/test.png"

# Test 3: Upload the test image
echo ""
echo "3. Testing image upload..."
RESPONSE=$(curl -s -X POST $BASE_URL/api/upload \
  -F "file=@/tmp/test.png" \
  -H "Accept: application/json")

echo "$RESPONSE" | python3 -m json.tool

# Extract video_id from response
VIDEO_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('video_id', ''))")

if [ ! -z "$VIDEO_ID" ]; then
    echo ""
    echo "✓ Upload successful! Video ID: $VIDEO_ID"

    # Test 4: Check upload status
    echo ""
    echo "4. Testing upload status..."
    curl -s $BASE_URL/api/upload/status/$VIDEO_ID | python3 -m json.tool

    # Test 5: Delete upload
    echo ""
    echo "5. Testing delete upload..."
    curl -s -X DELETE $BASE_URL/api/upload/$VIDEO_ID | python3 -m json.tool
else
    echo ""
    echo "✗ Upload failed"
fi

# Test 6: Test invalid file type
echo ""
echo "6. Testing invalid file type (should fail)..."
echo "This is a text file" > /tmp/test.txt
curl -s -X POST $BASE_URL/api/upload \
  -F "file=@/tmp/test.txt" \
  -H "Accept: application/json" | python3 -m json.tool

# Cleanup
rm -f /tmp/test.png /tmp/test.txt

echo ""
echo "============================================"
echo "✓ All tests completed!"
echo "============================================"
