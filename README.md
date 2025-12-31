# PeopleSay - Your Opinion, Amplified

A modern, comprehensive market research platform where real people share authentic opinions. Built for researchers who need quality insights and panelists who want to be heard.

## Architecture

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + Redis
- **Storage**: AWS S3
- **Payments**: Stripe

## Project Structure

```
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── api/          # API routes
│   │   ├── services/     # Business logic
│   │   ├── core/         # Config, security, dependencies
│   │   └── utils/        # Helpers
│   ├── alembic/          # Database migrations
│   └── tests/
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/          # App router pages
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities
│   │   ├── hooks/        # Custom hooks
│   │   └── types/        # TypeScript types
│   └── public/
└── docker-compose.yml    # Development environment
```

## Core Features

### 1. Poll Creation & Management
- Drag-and-drop form builder
- Multiple question types (A/B, ranking, open-ended, image, video)
- Templates library
- Advanced targeting rules

### 2. Panel Management
- User registration and profiling
- Demographic tracking
- Quality scoring system
- Fraud detection
- Credit/payment system for respondents

### 3. Response Collection
- Smart task distribution
- Real-time response capture
- Quality validation (attention checks, timing)
- Mobile-optimized interface

### 4. Analytics & Reporting
- Interactive visualizations
- Statistical significance testing
- AI-powered sentiment analysis
- Exportable PDF reports

### 5. Payment Infrastructure
- Client billing via Stripe
- Panelist wallet system
- Automated payouts

### 6. Admin Dashboard
- Response moderation
- Panel health metrics
- Support tools
- System monitoring

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Development Setup

1. Clone the repository
2. Start services with Docker:
   ```bash
   docker-compose up -d
   ```

3. Backend setup:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

4. Frontend setup:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Environment Variables

See `.env.example` files in `backend/` and `frontend/` directories.

## API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

## License

MIT
