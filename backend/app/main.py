from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, polls, responses, panel, payments, analytics, admin, uploads

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Market Research Platform API",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(polls.router, prefix="/api/polls", tags=["Polls"])
app.include_router(responses.router, prefix="/api/responses", tags=["Responses"])
app.include_router(panel.router, prefix="/api/panel", tags=["Panel"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["Uploads"])


@app.get("/")
def root():
    return {
        "message": "PickFu Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
