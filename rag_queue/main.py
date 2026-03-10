# ──────────────────────────────────────────────────────────────
# main.py — Entry point for the RAG Queue FastAPI application
# Run this file to start the server: python main.py
# ──────────────────────────────────────────────────────────────

# uvicorn: ASGI server that runs our FastAPI app
# It handles incoming HTTP requests and routes them to FastAPI
import uvicorn

# load_dotenv: Reads the .env file and loads key-value pairs
# into os.environ so they're accessible throughout the app
from dotenv import load_dotenv

# ⚠️ IMPORTANT: load_dotenv() is called BEFORE importing the app!
# Why? Because server.py (and its dependencies) need OPENAI_API_KEY
# to be available at import time. If we import 'app' first,
# the OpenAI client would initialize without the API key and fail.
load_dotenv()

# Now it's safe to import the FastAPI app from server.py
# At this point, OPENAI_API_KEY is already in os.environ ✅
from server import app


def main():
    """
    Start the FastAPI server using Uvicorn.

    Uvicorn is an ASGI server — it listens for HTTP requests
    and forwards them to our FastAPI app for handling.
    """
    uvicorn.run(
        app,               # The FastAPI application instance from server.py
        host="0.0.0.0",    # "0.0.0.0" = accept connections from ANY IP address
                           #   (not just localhost — useful for Docker/network access)
        port=8000          # Server runs on http://localhost:8000
    )


# ──────────────────────────────────────────────────────────────
# What does `if __name__ == "__main__"` do?
#
# Every Python file has a special variable called __name__.
#   - When you RUN this file directly (python main.py),
#     Python sets __name__ = "__main__"  →  main() gets called ✅
#   - When another file IMPORTS this file (import main),
#     Python sets __name__ = "main"  →  main() does NOT run ❌
#
# This prevents the server from accidentally starting when
# this file is imported by another module (e.g., for testing).
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
