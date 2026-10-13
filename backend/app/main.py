import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config.settings import settings
from .models.database import init_db
from .api.routes import api_router
from .utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database schema...")
    init_db()
    logger.info(f"AI Content Studio backend v{settings.VERSION} ready.")
    yield
    # Shutdown
    logger.info("Shutting down AI Content Studio backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent AI Video & Audio Generation Engine",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount generated static media assets
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
app.mount("/generated", StaticFiles(directory=settings.OUTPUT_DIR), name="generated")

# Mount API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "name": settings.PROJECT_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
