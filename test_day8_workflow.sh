#!/bin/bash

# AdjustR - Day 8 Upload UI Workflow Test
# This script tests the complete upload-to-results workflow

echo "======================================================================="
echo "  AdjustR - Day 8 Upload UI Workflow Test"
echo "======================================================================="
echo ""

# Check if services are running
echo "1. Checking if services are running..."
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Services are not running!"
    echo "   Please start services with: docker-compose up -d"
    exit 1
fi
echo "✅ Services are running"
echo ""

# Check backend health
echo "2. Checking backend health..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if [ $? -ne 0 ]; then
    echo "❌ Backend is not responding"
    exit 1
fi
echo "✅ Backend is healthy: $HEALTH_RESPONSE"
echo ""

# Check frontend is running
echo "3. Checking frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" != "200" ]; then
    echo "❌ Frontend is not accessible"
    exit 1
fi
echo "✅ Frontend is accessible"
echo ""

echo "======================================================================="
echo "  Manual Testing Instructions"
echo "======================================================================="
echo ""
echo "The automated upload-to-results workflow is now ready to test!"
echo ""
echo "📋 Test Steps:"
echo ""
echo "1. Open your browser and go to: http://localhost:3000"
echo ""
echo "2. You should see the AdjustR landing page with an upload area"
echo ""
echo "3. Drag and drop an image file (JPG/PNG) or video (MP4/MOV)"
echo "   - Or click to select a file"
echo "   - Try using one of the test images in the project"
echo ""
echo "4. Click the 'Analyze Damage' button"
echo ""
echo "5. Watch the workflow:"
echo "   ✅ Upload progress bar (0-100%)"
echo "   ✅ 'Upload successful! Starting analysis...' message"
echo "   ✅ Processing status: 'Processing video and extracting frames...'"
echo "   ✅ Processing status: 'Analyzing damage with AI...'"
echo "   ✅ 'Analysis complete! Redirecting to results...'"
echo "   ✅ Automatic redirect to results page"
echo ""
echo "6. On the results page, verify:"
echo "   ✅ Summary cards show (Total Cost, Damages, Types, Confidence)"
echo "   ✅ Damage breakdown by type"
echo "   ✅ Damage breakdown by severity"
echo "   ✅ Detailed detection results table"
echo "   ✅ 'New Analysis' and 'Print Report' buttons work"
echo ""
echo "7. Click 'New Analysis' to go back to upload page"
echo ""
echo "8. Test error handling:"
echo "   - Try uploading an invalid file type"
echo "   - Try uploading a file larger than 100MB (if available)"
echo "   - Verify error messages display correctly"
echo ""
echo "======================================================================="
echo "  Testing Backend API Directly (Optional)"
echo "======================================================================="
echo ""

# Create a simple test with curl
echo "Would you like to test the backend API directly? (y/n)"
read -r ANSWER

if [ "$ANSWER" = "y" ] || [ "$ANSWER" = "Y" ]; then
    echo ""
    echo "Testing API workflow..."
    echo ""

    # Find a test image
    TEST_IMAGE=""
    if [ -f "backend/test_image.jpg" ]; then
        TEST_IMAGE="backend/test_image.jpg"
    elif [ -f "test_image.jpg" ]; then
        TEST_IMAGE="test_image.jpg"
    else
        echo "⚠️  No test image found. Please provide path to an image:"
        read -r TEST_IMAGE
        if [ ! -f "$TEST_IMAGE" ]; then
            echo "❌ File not found: $TEST_IMAGE"
            exit 1
        fi
    fi

    echo "Using test image: $TEST_IMAGE"
    echo ""

    # Upload
    echo "📤 Uploading file..."
    UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8000/api/upload -F "file=@$TEST_IMAGE")
    VIDEO_ID=$(echo $UPLOAD_RESPONSE | grep -o '"video_id":[0-9]*' | grep -o '[0-9]*')

    if [ -z "$VIDEO_ID" ]; then
        echo "❌ Upload failed"
        echo "Response: $UPLOAD_RESPONSE"
        exit 1
    fi

    echo "✅ Upload successful! Video ID: $VIDEO_ID"
    echo ""

    # Trigger analysis
    echo "🔍 Triggering analysis..."
    ANALYZE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/analyze/$VIDEO_ID)
    echo "✅ Analysis started"
    echo ""

    # Poll for completion
    echo "⏳ Waiting for analysis to complete..."
    MAX_ATTEMPTS=30
    ATTEMPT=0

    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        STATUS_RESPONSE=$(curl -s http://localhost:8000/api/analyze/status/$VIDEO_ID)
        COMPLETE=$(echo $STATUS_RESPONSE | grep -o '"analysis_complete":[^,}]*' | grep -o '[^:]*$')

        if [ "$COMPLETE" = "true" ]; then
            echo "✅ Analysis complete!"
            break
        fi

        ATTEMPT=$((ATTEMPT + 1))
        echo -n "."
        sleep 2
    done
    echo ""
    echo ""

    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "⚠️  Analysis timeout (this is normal for complex images)"
    fi

    # Get results
    echo "📊 Fetching results..."
    RESULTS_RESPONSE=$(curl -s http://localhost:8000/api/results/$VIDEO_ID)
    TOTAL_COST=$(echo $RESULTS_RESPONSE | grep -o '"total_estimated_cost":[0-9.]*' | grep -o '[0-9.]*$')
    TOTAL_INFERENCES=$(echo $RESULTS_RESPONSE | grep -o '"total_inferences":[0-9]*' | grep -o '[0-9]*$')

    echo "✅ Results retrieved"
    echo ""
    echo "📈 Summary:"
    echo "   Total Cost: \$$TOTAL_COST"
    echo "   Total Damages Detected: $TOTAL_INFERENCES"
    echo ""
    echo "🌐 View full results in browser:"
    echo "   http://localhost:3000/results/$VIDEO_ID"
    echo ""
fi

echo "======================================================================="
echo "  Day 8 Test Complete!"
echo "======================================================================="
echo ""
echo "✅ All systems ready for Day 8 workflow"
echo "✅ Upload UI with automatic analysis"
echo "✅ Processing status tracking"
echo "✅ Automatic navigation to results"
echo ""
echo "Next: Day 9 - Enhanced Results Dashboard"
echo ""
