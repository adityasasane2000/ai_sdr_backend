from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.mongo_auth import auth_router
from app.mongo_routers import users, channels, prospects

app = FastAPI(title="AI SDR Platform API - MongoDB")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(channels.router, prefix="/channels", tags=["Channels"])
app.include_router(prospects.router, prefix="/prospects", tags=["Prospects"])

@app.get("/")
def read_root():
    return {"message": "Welcome to AI SDR Platform API - MongoDB Edition"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mongo_main:app", host="0.0.0.0", port=8000, reload=True)
