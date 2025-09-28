# Main FastAPI application for DyslexiQuest

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings, get_environment_info
from app.utils.session_manager import session_manager

# Rate limiting middleware (simple implementation)
from collections import defaultdict
import time


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    
    # Startup
    logger.info("🚀 Starting DyslexiQuest API...")
    logger.info(f"Environment: {get_environment_info()}")
    
    # Initialize components
    try:
        # Any startup initialization can go here
        logger.info("✅ All components initialized successfully")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down DyslexiQuest API...")
    
    # Cleanup
    try:
        # Clean up any resources
        logger.info(f"📊 Final session stats: {session_manager.get_session_stats()}")
        logger.info("✅ Shutdown completed successfully")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title="DyslexiQuest API",
    description="DyslexiQuest: A dyslexia-friendly text adventure game powered by AI, designed for children",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


request_counts = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting middleware"""
    
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests (older than 1 minute)
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip] 
        if current_time - req_time < 60
    ]
    
    # Check rate limit
    if len(request_counts[client_ip]) >= settings.rate_limit_per_minute:
        return JSONResponse(
            status_code=429,
            content={
                "error": "RateLimitExceeded",
                "message": "Too many requests. Please wait before trying again.",
                "retry_after": 60
            }
        )
    
    # Add current request
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response


# Include API routes
app.include_router(router, prefix="/api", tags=["Game"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    
    return {
        "message": "🎮 Welcome to DyslexiQuest! 🎮",
        "description": "DyslexiQuest: A dyslexia-friendly text adventure game powered by AI",
        "version": "1.0.0",
        "endpoints": {
            "start_game": "/api/start",
            "next_turn": "/api/next", 
            "backtrack": "/api/backtrack",
            "end_game": "/api/end",
            "health": "/api/health",
            "documentation": "/docs"
        },
        "features": [
            "🧠 AI-powered storytelling",
            "♿ Dyslexia-friendly design", 
            "📚 Educational vocabulary",
            "🔄 Backtracking support",
            "🛡️ Child-safe content filtering",
            "🎯 Puzzle-based gameplay"
        ]
    }


@app.get("/health")
async def health():
    """Simple health check endpoint"""
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "session_count": session_manager.get_session_count()
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    
    return JSONResponse(
        status_code=404,
        content={
            "error": "NotFound",
            "message": "The requested endpoint was not found",
            "available_endpoints": [
                "/api/start", "/api/next", "/api/backtrack", 
                "/api/end", "/api/health", "/docs"
            ]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    
    logger.error(f"Internal server error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An internal server error occurred. Please try again later.",
            "support": "If this persists, please report the issue."
        }
    )


# Add middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for debugging"""
    
    start_time = time.time()
    
    # Skip logging for health checks
    if request.url.path in ["/health", "/api/health"]:
        return await call_next(request)
    
    logger.info(f"📥 {request.method} {request.url.path} - {request.client.host}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"📤 {response.status_code} - {process_time:.3f}s")
    
    return response


if __name__ == "__main__":
    """Run the application directly"""
    
    logger.info("🎮 Starting DyslexiQuest API server...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level,
        reload=True  # Set to False in production
    )
