from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.core.config import settings

def setup_cors(app: FastAPI):
    """Configure CORS settings for FastAPI app"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Load from env
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )
