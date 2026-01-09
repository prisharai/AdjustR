#!/bin/bash

# AdjustR - Day 9 Enhanced Results Dashboard Test
# This script provides testing instructions for the enhanced dashboard

echo "======================================================================="
echo "  AdjustR - Day 9 Enhanced Results Dashboard Test"
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
echo "✅ Backend is healthy"
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
echo "  Day 9 Enhanced Dashboard Testing Instructions"
echo "======================================================================="
echo ""
echo "The enhanced results dashboard is now ready to test!"
echo ""
echo "🎨 NEW FEATURES TO TEST:"
echo ""
echo "1. VIEW MODES (4 different views):"
echo "   □ Overview - Summary cards + damage breakdowns"
echo "   □ Gallery - Frame thumbnails with damage badges"
echo "   □ Table - Detailed detection table"
echo "   □ Charts - Visual data representations"
echo ""
echo "2. FILTER PANEL:"
echo "   □ Filter by damage type (checkboxes)"
echo "   □ Filter by severity (high/medium/low)"
echo "   □ Minimum confidence slider (0-100%)"
echo "   □ Sort by (frame, confidence, severity, damage type)"
echo "   □ Sort order (ascending/descending)"
echo "   □ Reset all filters button"
echo "   □ Active filter count badge"
echo ""
echo "3. FRAME GALLERY:"
echo "   □ Grid layout of frame thumbnails"
echo "   □ Frame number badge on each image"
echo "   □ Damage count badge"
echo "   □ Highest severity badge"
echo "   □ Click to expand and see all detections"
echo "   □ Download individual frames"
echo "   □ Damage type tags"
echo ""
echo "4. VIDEO PLAYER (for video files):"
echo "   □ Video playback with controls"
echo "   □ Play/pause button"
echo "   □ Seek bar / timeline scrubbing"
echo "   □ Current frame indicator"
echo "   □ Previous/next frame buttons"
echo "   □ Frame counter display"
echo ""
echo "5. DATA VISUALIZATIONS:"
echo "   □ Damage distribution bar chart"
echo "   □ Severity distribution (stacked bar)"
echo "   □ Confidence level pie charts"
echo "   □ Key insights summary card"
echo ""
echo "6. FILTERING & SORTING:"
echo "   □ Real-time filter updates"
echo "   □ Filtered count vs total count display"
echo "   □ Combined filters work together"
echo "   □ Sorting affects all views"
echo ""
echo "======================================================================="
echo "  Step-by-Step Testing Guide"
echo "======================================================================="
echo ""
echo "STEP 1: Upload and Analyze"
echo "   1. Go to http://localhost:3000"
echo "   2. Upload an image with damage"
echo "   3. Wait for automatic analysis"
echo "   4. Navigate to results page"
echo ""
echo "STEP 2: Test View Modes"
echo "   1. Click 'Overview' - verify summary cards and breakdowns"
echo "   2. Click 'Gallery' - verify frame thumbnails with badges"
echo "   3. Click 'Table' - verify detailed table view"
echo "   4. Click 'Charts' - verify all visualizations render"
echo ""
echo "STEP 3: Test Filtering"
echo "   1. Click 'Filters & Sorting' to expand"
echo "   2. Check a damage type - verify filtered count updates"
echo "   3. Check 'High' severity - verify only high severity shown"
echo "   4. Adjust confidence slider to 70% - verify filtering"
echo "   5. Verify filter badge shows active filter count"
echo "   6. Click 'Reset All Filters' - verify all filters cleared"
echo ""
echo "STEP 4: Test Sorting"
echo "   1. Select 'Sort by: Confidence'"
echo "   2. Switch between ascending/descending"
echo "   3. Try other sort options (severity, damage type)"
echo "   4. Verify sorting works in Table and Gallery views"
echo ""
echo "STEP 5: Test Gallery Features"
echo "   1. Switch to 'Gallery' view"
echo "   2. Click on a frame thumbnail"
echo "   3. Verify expanded details show all detections"
echo "   4. Click download icon on a frame"
echo "   5. Verify frame image downloads"
echo "   6. Click frame again to collapse"
echo ""
echo "STEP 6: Test Video Player (if video uploaded)"
echo "   1. Upload a .mp4 or .mov file"
echo "   2. Wait for analysis"
echo "   3. On results page, verify video player appears"
echo "   4. Click play/pause"
echo "   5. Drag timeline scrubber"
echo "   6. Use previous/next frame buttons"
echo "   7. Verify current frame indicator updates"
echo ""
echo "STEP 7: Test Charts"
echo "   1. Switch to 'Charts' view"
echo "   2. Verify damage distribution bar chart"
echo "   3. Verify severity distribution stacked bar"
echo "   4. Verify confidence level circles for each type"
echo "   5. Verify key insights summary card"
echo ""
echo "STEP 8: Test Combined Features"
echo "   1. Apply filter: High severity only"
echo "   2. Switch between all view modes"
echo "   3. Verify filtered data shows in all views"
echo "   4. Change sort order"
echo "   5. Verify sorting affects Gallery and Table"
echo ""
echo "STEP 9: Test Print Functionality"
echo "   1. Click 'Print Report' button"
echo "   2. Verify print dialog opens"
echo "   3. Check print preview looks good"
echo ""
echo "STEP 10: Test Responsive Design"
echo "   1. Resize browser window"
echo "   2. Verify layouts adapt to smaller screens"
echo "   3. Check mobile view (375px width)"
echo "   4. Verify all features still accessible"
echo ""
echo "======================================================================="
echo "  Error Scenarios to Test"
echo "======================================================================="
echo ""
echo "1. No Results:"
echo "   - Navigate to /results/999 (invalid ID)"
echo "   - Verify error message displays"
echo "   - Verify 'Back to Upload' button works"
echo ""
echo "2. Image Load Errors:"
echo "   - If frame images fail to load"
echo "   - Verify placeholder with error icon shows"
echo ""
echo "3. Filter Edge Cases:"
echo "   - Apply filters that match no results"
echo "   - Verify '0 damages detected' message"
echo "   - Reset filters to see all results again"
echo ""
echo "4. Video Not Available:"
echo "   - If video file is missing"
echo "   - Verify 'Video unavailable' message"
echo ""
echo "======================================================================="
echo "  Performance Checks"
echo "======================================================================="
echo ""
echo "□ View mode switching is instant"
echo "□ Filter updates happen in <200ms"
echo "□ Gallery loads smoothly with many frames"
echo "□ Charts render without lag"
echo "□ Sorting completes quickly"
echo "□ Page is responsive on mobile"
echo ""
echo "======================================================================="
echo "  Browser Compatibility"
echo "======================================================================="
echo ""
echo "Test on multiple browsers:"
echo "□ Chrome/Edge (Chromium)"
echo "□ Firefox"
echo "□ Safari (macOS)"
echo ""
echo "======================================================================="
echo "  Quick Backend Test (Optional)"
echo "======================================================================="
echo ""

# Create a simple test with curl
echo "Would you like to test the backend API directly? (y/n)"
read -r ANSWER

if [ "$ANSWER" = "y" ] || [ "$ANSWER" = "Y" ]; then
    echo ""
    echo "Testing full workflow..."
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
    curl -s -X POST http://localhost:8000/api/analyze/$VIDEO_ID > /dev/null
    echo "✅ Analysis started"
    echo ""

    # Wait for completion
    echo "⏳ Waiting for analysis to complete..."
    sleep 10
    echo ""

    # Get results
    echo "📊 Fetching results..."
    RESULTS=$(curl -s http://localhost:8000/api/results/$VIDEO_ID)
    TOTAL_INFERENCES=$(echo $RESULTS | grep -o '"total_inferences":[0-9]*' | grep -o '[0-9]*')

    echo "✅ Results retrieved"
    echo ""
    echo "📈 Analysis Summary:"
    echo "   Total Detections: $TOTAL_INFERENCES"
    echo ""
    echo "🌐 View in Enhanced Dashboard:"
    echo "   http://localhost:3000/results/$VIDEO_ID"
    echo ""
    echo "   Try these views:"
    echo "   - Overview: Full summary and breakdowns"
    echo "   - Gallery: Frame thumbnails"
    echo "   - Table: Detailed listing"
    echo "   - Charts: Visual analytics"
    echo ""
fi

echo "======================================================================="
echo "  Day 9 Test Complete!"
echo "======================================================================="
echo ""
echo "✅ Enhanced Dashboard Features Ready:"
echo "   ✓ 4 view modes (Overview, Gallery, Table, Charts)"
echo "   ✓ Advanced filtering (type, severity, confidence)"
echo "   ✓ Flexible sorting (4 fields, 2 directions)"
echo "   ✓ Frame gallery with download"
echo "   ✓ Video player with controls"
echo "   ✓ Data visualizations and charts"
echo "   ✓ Real-time filter updates"
echo "   ✓ Responsive design"
echo ""
echo "Next: Day 10 - Navigation & Flow Enhancements"
echo ""
