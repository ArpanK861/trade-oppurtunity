"""
Trade Opportunities API — Server Entry Point
Run with: python run.py
"""
import uvicorn

from app.config import settings


def main() -> None:
    """Start the Uvicorn server."""
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_includes=[".env"],
        log_level="info",
    )


if __name__ == "__main__":
    main()
