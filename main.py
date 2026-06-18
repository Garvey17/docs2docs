from fastapi import FastAPI
from config.logging_config import get_logger
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

#Setup logging 
logger = get_logger(__name__)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.cors_origins_list,
    # allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting Docs to Docs.....')
    yield

@app.get('/health')
async def healthcheck():
    """Returns to check is the server is health"""

    return {
        "message": "Health check passes, app is healthy", 
        "app name": "Docs to Docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=True,
    )