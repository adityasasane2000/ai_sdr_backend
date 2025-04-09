from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models
from app.database import engine
from app.auth import auth_router
from app.routers import users, channels, prospects

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI SDR Platform API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(channels.router, prefix="/channels", tags=["Channels"])
app.include_router(prospects.router, prefix="/prospects", tags=["Prospects"])

# Simple API check
@app.get("/")
def read_root():
    return {"message": "Welcome to AI SDR Platform API"}

# Run locally
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
