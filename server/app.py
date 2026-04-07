"""
InfraMind server entry point.
This file satisfies the openenv validate requirement for server/app.py.
The actual FastAPI app is in the root server.py file.
"""
import sys
import os

# Add parent directory to path so root server.py is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from server import app  # noqa: F401 — re-export for openenv


def main():
    """Entry point for openenv validate and uvicorn."""
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 7860)),
        workers=1,
    )


if __name__ == "__main__":
    main()
