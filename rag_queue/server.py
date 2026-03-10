# ──────────────────────────────────────────────────────────
# server.py — FastAPI Server for RAG Queue
# ──────────────────────────────────────────────────────────
# This file creates a simple API with 3 endpoints:
#   1. GET  /              → Health check
#   2. POST /chat          → Submit a question (queues it)
#   3. GET  /result/{id}   → Fetch the answer by job ID
# ──────────────────────────────────────────────────────────

from fastapi import FastAPI, Query        # FastAPI framework + Query parameter helper
from rq.job import Job                    # RQ Job class to fetch job status/results
from client.rq_client import queue, redis_connection  # Our Redis queue + connection
from queues.worker import process_query   # The background function that does the RAG work


# ──────────────── Create the FastAPI App ────────────────

app = FastAPI(
    title="Async RAG Queue API",
    description="Submit queries asynchronously using Redis Queue"
)


# ──────────────── Route 1: Health Check ────────────────

@app.get("/")
def health_check():
    """Simple health check — confirms the server is alive."""
    return {"status": "Server is up and running"}


# ──────────────── Route 2: Submit a Query ────────────────

@app.post("/chat")
def chat(user_query: str = Query(..., description="Your question")):
    """
    Accepts a user question and pushes it into the Redis Queue.
    Returns a Job ID immediately — the server is NOT blocked.
    The actual AI processing happens in the background via the RQ Worker.
    """

    # Push the task into Redis Queue
    # This calls process_query(user_query) in the background worker
    job = queue.enqueue(process_query, user_query)

    # Return the job ID so the user can check the result later
    return {
        "message": "Your query has been queued for processing ⏳",
        "job_id": job.id,
        "status": "queued",
        "tip": f"Check your result at: GET /result/{job.id}"
    }


# ──────────────── Route 3: Get the Result ────────────────

@app.get("/result/{job_id}")
def get_result(job_id: str):
    """
    Fetch the result of a previously submitted job using its ID.

    Possible statuses:
      - queued   → Job is waiting in the queue
      - started  → Worker picked it up, processing now
      - finished → Done! Result is ready
      - failed   → Something went wrong
    """

    # Try to find the job in Redis by its ID
    try:
        job = Job.fetch(job_id, connection=redis_connection)
    except Exception:
        return {"error": "Job not found. Check your Job ID."}

    # Check the job's current status and return accordingly
    if job.is_finished:
        return {
            "job_id": job_id,
            "status": "finished ✅",
            "result": job.result
        }

    if job.is_failed:
        return {
            "job_id": job_id,
            "status": "failed ❌",
            "error": str(job.exc_info)
        }

    # Still in progress (queued or started)
    return {
        "job_id": job_id,
        "status": job.get_status(),
        "message": "Still processing... try again in a few seconds ⏳"
    }