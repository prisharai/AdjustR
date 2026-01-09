# AdjustR - 2-Week MVP Project Plan

**Last Updated**: January 9, 2026
**Status**: Day 9 Complete - Enhanced Results Dashboard
**Timeline**: 14 Days Total

---

## Executive Summary

**Product**: AdjustR - AI-powered property damage assessment tool for insurance adjusters
**Goal**: Launch functional MVP in 2 weeks with video upload, damage detection, cost estimation, and PDF reports
**Tech Stack**: FastAPI + Next.js + PostgreSQL + YOLOv8 + Docker
**Budget**: <$25/month (AWS free tier)

---

## Progress Tracker

### Week 1: Backend Foundation ✅ COMPLETE
- [x] Day 1: Project Setup & Infrastructure
- [x] Day 2: Database & S3 Configuration
- [x] Day 3: File Upload API
- [x] Day 4: Video Processing
- [x] Day 5: YOLOv8 Integration
- [x] Day 6: Damage Detection Pipeline
- [x] Day 7: Results API

### Week 2: Frontend & Integration
- [x] Day 8: Upload UI
- [x] Day 9: Results Dashboard
- [ ] Day 10: Navigation & Flow
- [ ] Day 11: Testing & Bug Fixes
- [ ] Day 12: Polish & Optimization
- [ ] Day 13: Final Testing & QA
- [ ] Day 14: Deployment

---

## Daily Breakdown

## ✅ Day 1 Complete - Project Setup (Jan 9)

### Completed
- FastAPI backend with health check
- Next.js frontend with landing page
- PostgreSQL database in Docker
- Docker Compose orchestration
- Database models (Videos, Inferences, Reports)
- TailwindCSS with AdjustR branding

### Files Created
- `backend/app/main.py` - FastAPI application
- `backend/app/models.py` - SQLAlchemy models
- `backend/app/schemas.py` - Pydantic schemas
- `frontend/src/pages/index.tsx` - Landing page
- `docker-compose.yml` - Multi-container setup

---

## ✅ Day 2 Complete - Database & S3 Setup (Jan 9)

### Completed
- Database initialization with Alembic
- S3 utility module with local fallback
- File validation utilities
- Docker entrypoint for database setup
- Database tables auto-created on startup

### Files Created
- `backend/app/init_db.py` - Database initialization
- `backend/alembic/` - Migration framework
- `backend/app/utils/s3.py` - S3 client with fallback
- `backend/app/utils/file_validation.py` - File validators
- `backend/docker-entrypoint.sh` - Startup script

### Database Schema
```sql
videos: id, filename, s3_url, upload_timestamp, status, file_size, duration, frame_count
inferences: id, video_id, frame_number, frame_url, damage_type, severity, confidence, bounding_box
reports: id, video_id, total_estimated_cost, damage_summary, pdf_url
```

### Next Steps
- Day 3: Implement file upload endpoint
- Test upload with images and videos
- Store files in S3 or local storage

---

## 📅 Day 3 - File Upload API (Next)

### Objectives
- Create upload router
- Accept video/image files
- Validate file type and size
- Store in S3/local storage
- Save metadata to database

### Tasks
1. **Create Upload Router** (`backend/app/routers/upload.py`)
   ```python
   @router.post("/upload")
   async def upload_file(file: UploadFile, db: Session):
       # Validate file
       # Upload to S3
       # Create database record
       # Return video_id
   ```

2. **File Processing**
   - Max size: 100MB
   - Allowed: .mp4, .mov, .jpg, .png
   - Generate unique filenames
   - Handle upload errors

3. **Response Schema**
   ```json
   {
     "video_id": 1,
     "filename": "damage.mp4",
     "s3_url": "https://...",
     "status": "uploaded"
   }
   ```

4. **Testing**
   - Test with curl/Postman
   - Verify database record
   - Check S3/local storage

### Success Criteria
- ✅ Upload completes in <15 seconds
- ✅ Files stored correctly
- ✅ Database record created
- ✅ Error handling works

---

## 📅 Day 4 - Video Processing

### Objectives
- Extract keyframes from videos
- Process background tasks
- Store frames in S3

### Tasks
1. **Video Processor** (`backend/ml/video_processor.py`)
   - Use OpenCV to extract frames
   - Extract every 2 seconds
   - Save as JPG
   - Upload to S3

2. **Background Processing**
   - Use FastAPI BackgroundTasks
   - Update video status
   - Handle errors gracefully

3. **Frame Management**
   - Naming: `{video_id}/frame_{n}.jpg`
   - Update frame_count in database

### Success Criteria
- ✅ Keyframes extracted correctly
- ✅ Processing completes in <30s for 1-min video
- ✅ Status updates work

---

## 📅 Day 5 - YOLOv8 Integration

### Objectives
- Install and configure YOLOv8
- Run inference on test images
- Map detections to damage types

### Tasks
1. **Detector Module** (`backend/ml/detector.py`)
   ```python
   from ultralytics import YOLO

   class DamageDetector:
       def __init__(self):
           self.model = YOLO('yolov8n.pt')

       def detect(self, image_path):
           results = self.model(image_path)
           return parse_results(results)
   ```

2. **Damage Mapping**
   ```python
   DAMAGE_MAP = {
       'crack': 'Ceiling Crack',
       'mold': 'Mold',
       'water': 'Water Damage'
   }
   ```

3. **Severity Logic**
   - Low: confidence < 0.5
   - Medium: confidence 0.5-0.75
   - High: confidence > 0.75

### Success Criteria
- ✅ Model loads successfully
- ✅ Inference runs on images
- ✅ Bounding boxes extracted

---

## 📅 Day 6 - Damage Detection Pipeline

### Objectives
- Run inference on all frames
- Store results in database
- Calculate cost estimates

### Tasks
1. **Analysis Router** (`backend/app/routers/analysis.py`)
   ```python
   @router.post("/analyze/{video_id}")
   async def analyze_video(video_id: int, db: Session):
       # Get all frames
       # Run detection
       # Save inferences
       # Calculate costs
   ```

2. **Cost Estimator** (`backend/ml/cost_estimator.py`)
   ```python
   COSTS = {
       'Ceiling Crack': 1300,
       'Mold': 2400,
       'Water Damage': 1800
   }
   ```

3. **Batch Processing**
   - Process all frames
   - Aggregate results
   - Return summary

### Success Criteria
- ✅ Analysis completes in <10s
- ✅ All inferences saved
- ✅ Cost calculation works

---

## 📅 Day 7 - Results API

### Objectives
- Create results endpoint
- Optimize queries
- Add error handling

### Tasks
1. **Results Router**
   ```python
   @router.get("/results/{video_id}")
   async def get_results(video_id: int, db: Session):
       # Fetch video + inferences
       # Calculate summary
       # Return structured data
   ```

2. **Optimization**
   - Use eager loading
   - Add database indexes
   - Cache common queries

### Success Criteria
- ✅ Response time <2s
- ✅ Complete data returned
- ✅ Error handling works

---

## 📅 Day 8 - Upload UI

### Objectives
- Create upload page with drag-and-drop
- Show upload progress
- Navigate to results

### Tasks
1. **Upload Component**
   - Use react-dropzone
   - Show progress bar
   - Handle errors

2. **API Integration**
   - Call upload endpoint
   - Parse response
   - Store video_id

### Success Criteria
- ✅ Drag-and-drop works
- ✅ Progress indicator accurate
- ✅ Errors displayed clearly

---

## 📅 Day 9 - Results Dashboard

### Objectives
- Display damage data
- Show video preview
- Display cost breakdown

### Tasks
1. **Results Page**
   - Video player
   - Damage table
   - Cost summary

2. **Data Display**
   - Frame thumbnails
   - Confidence scores
   - Severity badges

### Success Criteria
- ✅ All data displayed
- ✅ Video plays correctly
- ✅ Responsive design

---

## 📅 Day 10 - Navigation & Flow

### Objectives
- Connect all pages
- Add loading states
- Handle errors

### Tasks
1. **Routing**
   - Upload → Analysis → Results
   - Automatic redirects

2. **State Management**
   - Track upload status
   - Show progress

### Success Criteria
- ✅ Complete flow works
- ✅ Loading states clear
- ✅ Navigation intuitive

---

## 📅 Day 11 - Testing & Bug Fixes

### Objectives
- End-to-end testing
- Fix bugs
- Improve UX

### Tasks
1. **Testing**
   - Test all workflows
   - Various file types
   - Error scenarios

2. **Bug Fixes**
   - Fix critical bugs
   - Improve error messages

### Success Criteria
- ✅ Upload success >90%
- ✅ Analysis time <10s
- ✅ No critical bugs

---

## 📅 Day 12 - Polish & Optimization

### Objectives
- UI/UX improvements
- Performance optimization
- Code cleanup

### Tasks
1. **Polish**
   - Refine animations
   - Improve error messages
   - Add tooltips and help text

2. **Optimization**
   - Image loading optimization
   - Bundle size reduction
   - Caching strategies

### Success Criteria
- ✅ Smooth animations
- ✅ Fast load times
- ✅ Professional appearance

---

## 📅 Day 13 - Final Testing & QA

### Objectives
- Comprehensive testing
- Cross-browser testing
- Production readiness

### Tasks
1. **Testing**
   - End-to-end testing
   - Edge case handling
   - Performance testing

### Success Criteria
- ✅ All features working
- ✅ No critical bugs
- ✅ Ready for production

---

## 📅 Day 14 - Deployment

### Objectives
- Deploy to AWS EC2
- Configure production
- Launch soft beta

### Tasks
1. **AWS Setup**
   - Launch EC2 (t3.medium)
   - Install Docker
   - Configure SSL

2. **Deployment**
   - Build images
   - Deploy with docker-compose
   - Test in production

### Success Criteria
- ✅ App accessible via HTTPS
- ✅ Complete workflow works
- ✅ Ready for beta users

---

## Tech Stack

### Backend
- FastAPI 0.104.1
- Python 3.11
- SQLAlchemy 2.0.23
- PostgreSQL 15
- YOLOv8 (Ultralytics)
- OpenCV 4.8
- WeasyPrint 60.1

### Frontend
- Next.js 14.0.4
- React 18.2.0
- TypeScript 5.3.3
- TailwindCSS 3.3.6
- Axios 1.6.2

### Infrastructure
- Docker & Docker Compose
- AWS S3 (optional)
- AWS EC2 (deployment)

---

## API Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/health` | Health check | ✅ Done |
| POST | `/api/upload` | Upload file | ✅ Done |
| POST | `/api/analyze/{video_id}` | Analyze damage | ✅ Done |
| GET | `/api/results/{video_id}` | Get results | ✅ Done |
| GET | `/api/videos` | List all videos | 📅 Day 10 |

---

## Database Schema (✅ Implemented)

### Videos Table
```sql
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    s3_url VARCHAR(500) NOT NULL,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'uploaded',
    file_size INTEGER,
    duration FLOAT,
    frame_count INTEGER
);
```

### Inferences Table
```sql
CREATE TABLE inferences (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    frame_number INTEGER,
    frame_url VARCHAR(500),
    damage_type VARCHAR(100),
    severity VARCHAR(50),
    confidence FLOAT,
    bounding_box JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Reports Table
```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    total_estimated_cost DECIMAL(10,2),
    damage_summary JSONB,
    pdf_url VARCHAR(500),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Quick Commands

```bash
# Start all services
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Access database
docker exec -it adjustr-postgres psql -U adjustr -d adjustr

# Run migrations
docker exec -it adjustr-backend alembic upgrade head

# Initialize database
docker exec -it adjustr-backend python -c "from app.init_db import init_db; init_db()"
```

---

## Success Metrics

### Technical Metrics
- Upload success rate: >90%
- Analysis time: <10 seconds
- Response time: <2 seconds
- Uptime: >99%

### User Metrics (Beta)
- User satisfaction: ≥4/5
- Successful workflows: >80%
- Repeat usage: >50%

---

## Risk Mitigation

### Technical Risks
1. **ML Accuracy**: Use pretrained YOLOv8, focus on proof-of-concept
2. **Processing Time**: Limit video length, extract frames at 2s intervals
3. **AWS Costs**: Use free tier, set billing alerts
4. **PDF Generation**: Use simple HTML templates

### Scope Risks
1. **Feature Creep**: Strictly P0 features only
2. **Timeline**: Daily progress reviews, cut scope if needed

---

## Resources

### Development
- Solo developer, full-time (2 weeks)
- MacBook with 16GB+ RAM
- Docker Desktop

### Cloud (Production)
- AWS EC2: t3.medium (~$30/month, use free tier)
- AWS S3: ~$1-5/month
- Total: <$25/month target

---

## Post-MVP Roadmap

### Week 3-4: Iteration
- Gather beta feedback
- Fix bugs
- Optimize ML accuracy

### Month 2: Features
- User authentication
- Multiple assessments
- User annotations
- Export to insurance forms

### Month 3+: Growth
- Marketing to insurance companies
- API integrations
- Mobile app
- Fine-tune ML model

---

## Current Status

**Days Complete**: 9/14 (64%)
**Week 1 Progress**: 100% (7/7 days) ✅
**Week 2 Progress**: 29% (2/7 days)

### Completed (Week 1 + Days 8-9)
- ✅ Project infrastructure (Day 1)
- ✅ Database setup (Day 2)
- ✅ S3 utilities (Day 2)
- ✅ Docker orchestration (Day 1)
- ✅ File upload API (Day 3)
- ✅ Video processing & keyframe extraction (Day 4)
- ✅ YOLOv8 damage detection (Day 5)
- ✅ Damage detection pipeline (Day 6)
- ✅ Results API with filtering & sorting (Day 7)
- ✅ Upload UI with automatic analysis (Day 8)
- ✅ Results page with navigation (Day 8)
- ✅ Enhanced results dashboard with 4 view modes (Day 9)
- ✅ Advanced filtering and sorting (Day 9)
- ✅ Frame gallery with download (Day 9)
- ✅ Video player component (Day 9)
- ✅ Data visualizations and charts (Day 9)

### In Progress
- 📅 Day 10: Navigation & Flow (Next)

### Blocked
- None

---

## Notes

- Using local storage fallback for development (no AWS required)
- Database auto-initializes on startup
- Hot reload enabled for rapid development
- All sensitive config in environment variables
- **Backend complete and production-ready**
- Week 2 focuses on frontend development

---

**Last Updated**: Day 9 Complete - January 9, 2026
**Next Milestone**: Day 10 - Navigation & Flow
**On Track**: Yes ✅

**Major Milestones Achieved**:
- ✅ Complete upload system (Day 3)
- ✅ Video processing pipeline (Day 4)
- ✅ YOLOv8 damage detection (Day 5)
- ✅ End-to-end analysis pipeline (Day 6)
- ✅ Advanced results API (Day 7)
- ✅ **Week 1 Complete - Backend Ready** 🎉
- ✅ Upload UI with automatic workflow (Day 8)
- ✅ **Working Upload-to-Results Flow** 🎉
- ✅ Enhanced results dashboard with 4 views (Day 9)
- ✅ **Professional Dashboard Interface** 🎉
