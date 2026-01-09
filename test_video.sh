#!/bin/bash

# Test script for video processing

BASE_URL="http://localhost:8000"

echo "============================================"
echo "Testing Video Processing"
echo "============================================"

# Check if ffmpeg is available (for creating test video)
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ffmpeg not found. Using simple test with image instead."
    echo ""

    # Create a simple test image
    echo "1. Creating test image..."
    echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > /tmp/test_damage.png

    # Upload image
    echo "2. Uploading image..."
    RESPONSE=$(curl -s -X POST $BASE_URL/api/upload \
      -F "file=@/tmp/test_damage.png" \
      -H "Accept: application/json")

    echo "$RESPONSE" | python3 -m json.tool

    VIDEO_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('video_id', ''))" 2>/dev/null)

    if [ ! -z "$VIDEO_ID" ]; then
        echo ""
        echo "✓ Upload successful! Video ID: $VIDEO_ID"
        echo "Waiting for processing..."

        sleep 3

        echo ""
        echo "3. Checking processing status..."
        curl -s $BASE_URL/api/upload/status/$VIDEO_ID | python3 -m json.tool

        echo ""
        echo "4. Checking stored frames..."
        docker exec -it adjustr-backend ls -lh uploads/frames/ 2>/dev/null || echo "  (Run from project root with docker)"
    fi

    # Cleanup
    rm -f /tmp/test_damage.png

else
    echo "1. Creating test video with ffmpeg..."

    # Create 5-second test video with colored frames
    ffmpeg -f lavfi -i color=c=red:s=640x480:d=5 -vf "drawtext=text='Test Video':fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" -pix_fmt yuv420p /tmp/test_video.mp4 -y &>/dev/null

    if [ $? -eq 0 ]; then
        echo "✓ Test video created"

        echo ""
        echo "2. Uploading video..."
        RESPONSE=$(curl -s -X POST $BASE_URL/api/upload \
          -F "file=@/tmp/test_video.mp4" \
          -H "Accept: application/json")

        echo "$RESPONSE" | python3 -m json.tool

        VIDEO_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('video_id', ''))" 2>/dev/null)

        if [ ! -z "$VIDEO_ID" ]; then
            echo ""
            echo "✓ Upload successful! Video ID: $VIDEO_ID"
            echo "Waiting for processing (may take 10-20 seconds)..."

            # Wait for processing
            MAX_WAIT=30
            WAITED=0

            while [ $WAITED -lt $MAX_WAIT ]; do
                sleep 2
                WAITED=$((WAITED + 2))

                STATUS=$(curl -s $BASE_URL/api/upload/status/$VIDEO_ID | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)

                echo "  Status: $STATUS (waited ${WAITED}s)"

                if [ "$STATUS" = "processed" ]; then
                    break
                fi
            done

            echo ""
            echo "3. Final status:"
            curl -s $BASE_URL/api/upload/status/$VIDEO_ID | python3 -m json.tool

            echo ""
            echo "4. Checking stored frames..."
            docker exec -it adjustr-backend ls -lh uploads/frames/ 2>/dev/null || echo "  (Run from project root with docker)"
        fi

        # Cleanup
        rm -f /tmp/test_video.mp4
    else
        echo "❌ Failed to create test video"
    fi
fi

echo ""
echo "============================================"
echo "✓ Test completed!"
echo "============================================"
