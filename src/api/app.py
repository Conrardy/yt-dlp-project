"""
FastAPI application entry point for YouTube Audio Downloader.

This module initializes and configures the FastAPI application, including:
- CORS middleware for cross-origin requests
- Static file serving for CSS and JavaScript
- Jinja2 template rendering for the web interface
- API router inclusion for REST endpoints
- Database initialization on startup

The application provides a modern web interface for downloading audio from
YouTube videos with real-time progress tracking via Server-Sent Events (SSE).

Attributes:
    app (FastAPI): The main FastAPI application instance
    templates (Jinja2Templates): Template renderer for HTML pages
    logger (Logger): Application logger for debugging and monitoring

Example:
    Run the server using uvicorn:
    
    >>> uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
    
    Or directly:
    
    >>> python run_server.py
"""

import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Audio Downloader",
    description="Web interface for downloading audio from YouTube videos",
    version="1.0.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
# Path from src/api/app.py: parent = src/api, parent.parent = src
static_dir = Path(__file__).parent.parent / "static"
templates_dir = Path(__file__).parent.parent / "templates"

# Create directories if they don't exist
static_dir.mkdir(parents=True, exist_ok=True)
templates_dir.mkdir(parents=True, exist_ok=True)

# Mount static files
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(templates_dir))

# Include API routes
app.include_router(router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Serve the main HTML page.
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTML response
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
async def startup_event():
    """
    Initialize application resources on startup.
    
    This lifecycle event handler is called when the FastAPI application starts.
    It performs the following initialization tasks:
    
    1. Creates and initializes the SQLite database connection
    2. Sets up the downloads table schema if it doesn't exist
    3. Creates necessary indexes for query performance
    
    Raises:
        Exception: Logs any initialization errors but doesn't prevent startup
                   to allow the application to handle missing database gracefully.
    """
    try:
        from .database import get_database
        db = get_database()
        await db.initialize()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up application resources on shutdown.
    
    This lifecycle event handler is called when the FastAPI application
    is shutting down. It performs cleanup tasks such as:
    
    1. Logging the shutdown event for monitoring
    2. Any pending database connections are automatically closed by aiosqlite
    
    Note:
        Background download tasks in progress will be terminated when the
        application shuts down. Consider implementing graceful shutdown
        handling for long-running downloads in production environments.
    """
    logger.info("Application shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
