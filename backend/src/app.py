import sys
from fastapi import FastAPI, Request, status
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.database import close_mongo_connection, connect_to_mongo
from backend.src.routes.revisions import router as revisions_router

# CURRENT_FILE = Path(__file__).resolve()
# SRC_ROOT = CURRENT_FILE.parent
# sys.path.append(str(SRC_ROOT))

@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_to_mongo() 
    yield
    close_mongo_connection()

app = FastAPI(
    title="Multi-Agent Core Engine API",
    description="Clinical note revised system.",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    print(f"[CRITICAL ERROR] Detected on path: {request.url.path}")
    print(f"Error Details: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal Server Error",
            "message": "A critical backend error occurred. Please contact system engineering support."
        }
    )

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bind routers
app.include_router(revisions_router)

@app.get("/", tags=["Root Health Check"])
async def root_health_check():
    return {
        "status": "healthy",
        "system": "Multi-Agent Clinical Engine",
        "environment_version": "2026-v1"
    }

if __name__ == "__main__":
    import uvicorn
    # Spin up development server on port 8000
    uvicorn.run("backend.src.app:app", host="0.0.0.0", port=8000, reload=True)