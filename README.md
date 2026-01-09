# AdjustR

**Turn photos into instant damage insights**

AdjustR is an AI-powered property damage assessment tool designed to streamline the insurance claims process. Upload property damage photos or videos and receive structured, reliable damage assessments with cost estimates in minutes.

## Features

- **Instant Upload**: Upload damage photos or videos (MP4, MOV, JPG, PNG)
- **AI-Powered Detection**: YOLOv8-based damage detection and classification
- **Cost Estimation**: Automatic repair cost estimation by damage type
- **Professional Reports**: Download structured PDF reports for insurance claims
- **Fast Processing**: Analysis completed in under 10 seconds

## Tech Stack

- **Frontend**: Next.js 14 + TypeScript + TailwindCSS
- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **ML**: YOLOv8 (Ultralytics), OpenCV
- **Storage**: AWS S3 (optional for production)
- **Infrastructure**: Docker + Docker Compose

## Prerequisites

- Docker Desktop installed
- 16GB+ RAM recommended (for ML models)
- Stable internet connection

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AdjustR-1
```

### 2. Start with Docker Compose

```bash
# Start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Backend API on http://localhost:8000
- Frontend web app on http://localhost:3000

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run backend (requires PostgreSQL running)
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Project Structure

```
AdjustR-1/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database connection
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   └── routers/          # API endpoints
│   ├── ml/                   # ML modules
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/            # Next.js pages
│   │   ├── components/       # React components
│   │   ├── services/         # API service
│   │   └── styles/           # CSS styles
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── projectplan.md            # Detailed implementation plan
└── README.md
```

## API Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/health` | Health check | ✅ Done |
| POST | `/api/upload` | Upload video/image | ✅ Done |
| GET | `/api/upload/status/{video_id}` | Get upload status | ✅ Done |
| DELETE | `/api/upload/{video_id}` | Delete upload | ✅ Done |
| POST | `/api/analyze/{video_id}` | Analyze damage | 📅 Day 6 |
| GET | `/api/results/{video_id}` | Get analysis results | 📅 Day 7 |
| POST | `/api/report/{video_id}` | Generate PDF report | 📅 Day 11 |
| GET | `/api/report/{video_id}/download` | Download PDF | 📅 Day 11 |

## Database Schema

### Videos Table
- `id`: Primary key
- `filename`: Original filename
- `s3_url`: Storage URL
- `upload_timestamp`: Upload time
- `status`: Processing status
- `file_size`: File size in bytes
- `duration`: Video duration
- `frame_count`: Number of frames

### Inferences Table
- `id`: Primary key
- `video_id`: Foreign key to videos
- `frame_number`: Frame index
- `damage_type`: Type of damage detected
- `severity`: low/medium/high
- `confidence`: Detection confidence score
- `bounding_box`: Detection coordinates

### Reports Table
- `id`: Primary key
- `video_id`: Foreign key to videos
- `total_estimated_cost`: Total repair cost
- `damage_summary`: JSON summary
- `pdf_url`: Report PDF URL
- `generated_at`: Generation timestamp

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Application
APP_NAME=AdjustR
DEBUG=True

# Database
DATABASE_URL=postgresql://adjustr:adjustr@postgres:5432/adjustr

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=adjustr-uploads-dev

# ML Model
YOLO_MODEL_PATH=yolov8n.pt
KEYFRAME_INTERVAL=2.0
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing
1. Visit http://localhost:3000
2. Upload a test image or video
3. Wait for analysis to complete
4. View results and download report

## Deployment

See [projectplan.md](projectplan.md) for detailed deployment instructions.

### Production Checklist
- [ ] Set up AWS S3 bucket
- [ ] Configure PostgreSQL (RDS or managed)
- [ ] Set up EC2 instance
- [ ] Configure SSL certificate
- [ ] Set environment variables
- [ ] Build Docker images
- [ ] Deploy with docker-compose

## Project Status

**Current Progress**: 36% (Day 5/14)
**Week 1**: 71% (5/7 days)

### Completed Features
- ✅ Day 1: Project setup, Docker, database models
- ✅ Day 2: Database initialization, S3 utilities, Alembic
- ✅ Day 3: File upload API with drag-and-drop UI
- ✅ Day 4: Video processing & keyframe extraction with OpenCV
- ✅ Day 5: YOLOv8 damage detection & cost estimation

### In Progress
- 🔄 Day 6: Damage detection pipeline integration

## Roadmap

### Current (MVP)
- ✅ Video/image upload (Day 3)
- ⏳ Video processing (Day 4)
- ⏳ Damage detection with YOLOv8 (Days 5-6)
- ⏳ Cost estimation (Day 6)
- ⏳ Results dashboard (Days 9-10)
- ⏳ PDF report generation (Days 11-12)

### Phase 2 (Weeks 3-4)
- User authentication
- Save and manage assessments
- Improved ML accuracy
- Mobile responsiveness

### Phase 3 (Month 2+)
- User annotations
- Custom damage types
- Export to insurance forms
- Mobile app

## Contributing

This is currently a solo project. Contributions welcome after MVP launch.

## License

Proprietary - All rights reserved

## Support

For issues or questions, contact the development team.

---

**Built with Claude Code**
