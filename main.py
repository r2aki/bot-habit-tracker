from fastapi import FastAPI
from api.api_v1.router import api_router
from core.config import settings
from db.base import Base
from db.session import engine
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from bot.bot_instance import start_bot_polling, stop_bot
from notifications.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    # Startup events
    print("Starting up application...")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created")

    # Start Telegram bot
    await start_bot_polling()
    print("Telegram bot started")

    # Start notification scheduler
    start_scheduler()
    print("Notification scheduler started")

    yield

    # Shutdown events
    print("Shutting down application...")

    # Stop notification scheduler
    stop_scheduler()
    print("Notification scheduler stopped")

    # Stop Telegram bot
    await stop_bot()
    print("Telegram bot stopped")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Habit Tracker API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}