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
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(channels.router, prefix="/api/channels", tags=["Channels"])
app.include_router(prospects.router, prefix="/api/prospects", tags=["Prospects"])

# Simple API check
@app.get("/api")
def read_root():
    return {"message": "Welcome to AI SDR Platform API"}

# Serve React frontend (after build)
frontend_build_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/build"))
static_dir = os.path.join(frontend_build_path, "static")

# Serve static files (JS/CSS etc.)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Catch-all route to serve index.html
@app.get("/{full_path:path}")
def serve_react_app(full_path: str):
    index_path = os.path.join(frontend_build_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "React build not found. Did you run npm run build?"}

# Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
