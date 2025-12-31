# PickFu Platform - Setup Guide

Complete setup instructions for the PickFu market research platform.

## Prerequisites

- Docker & Docker Compose (recommended)
- OR manual setup:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+
  - Redis 7+

## Quick Start with Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd Testing-
```

2. Create environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Update the environment variables in `backend/.env` and `frontend/.env` with your actual values (Stripe keys, AWS credentials, etc.)

4. Start all services:
```bash
docker-compose up -d
```

5. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

6. Access the applications:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Manual Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start PostgreSQL and Redis (ensure they're running)

6. Run migrations:
```bash
alembic upgrade head
```

7. Start the server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. Start development server:
```bash
npm run dev
```

## Database Schema

The platform uses PostgreSQL with the following main tables:

- `users` - User accounts (clients, panelists, admins)
- `panel_members` - Panelist profiles and demographics
- `polls` - Survey/poll definitions
- `questions` - Poll questions
- `responses` - Survey responses
- `response_answers` - Individual question answers
- `payments` - Client payments
- `payouts` - Panelist payouts
- `wallet_transactions` - Panelist wallet history

## User Roles

1. **Client** - Create polls and view results
2. **Panelist** - Complete surveys and earn money
3. **Admin** - Platform administration

## Initial Testing

### Create a Client Account
1. Go to http://localhost:3000/register
2. Select "Create polls and gather insights"
3. Complete registration

### Create a Panelist Account
1. Go to http://localhost:3000/register
2. Select "Earn money by answering surveys"
3. Complete registration
4. Fill out your profile at `/dashboard/panel/profile`

### Create Your First Poll (as Client)
1. Login as a client
2. Go to dashboard
3. Click "Create New Poll"
4. Add questions and configure settings
5. Publish the poll

### Complete a Survey (as Panelist)
1. Login as a panelist
2. View available surveys on dashboard
3. Click "Start Survey" on any available poll
4. Complete and submit

## Payment Integration

### Stripe Setup
1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe dashboard
3. Add keys to `backend/.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```
4. Add publishable key to `frontend/.env.local`:
   ```
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

### Webhook Configuration
1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Forward webhooks to local:
   ```bash
   stripe listen --forward-to localhost:8000/api/payments/webhook
   ```
3. Add webhook secret to `backend/.env`

## AWS S3 Setup (Optional)

For media uploads (images, videos):

1. Create an S3 bucket
2. Configure CORS for the bucket
3. Add credentials to `backend/.env`:
   ```
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-bucket-name
   ```

## Production Deployment

### Environment Variables

Ensure all sensitive values are changed from development defaults:
- `SECRET_KEY` - Use a strong random string
- Database credentials
- Stripe API keys
- AWS credentials

### Database Migrations

Always run migrations before deploying:
```bash
alembic upgrade head
```

### Frontend Build

Build the optimized production bundle:
```bash
cd frontend
npm run build
npm start
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Enable rate limiting
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists: `createdb pickfu_dev`

### Frontend Can't Connect to Backend
- Check NEXT_PUBLIC_API_URL in frontend/.env.local
- Ensure backend is running on correct port
- Check CORS configuration in backend

### Migrations Failing
- Drop and recreate database if in development
- Check alembic version: `alembic current`
- Verify all models are imported in alembic/env.py

## Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com
- Next.js Documentation: https://nextjs.org/docs
- Stripe API: https://stripe.com/docs/api
- PostgreSQL: https://www.postgresql.org/docs

## Support

For issues or questions, please create an issue in the repository.
