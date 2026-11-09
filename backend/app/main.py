"""
Product Hunter AI - Main Application Entry Point

Egyptian Electronics & Gadgets Market Intelligence Platform
"""

import uvicorn
from .api import app
from .core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
    )