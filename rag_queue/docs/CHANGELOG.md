# Changelog

## Changes Made - March 5, 2026

### Major Refactoring - Aligned with Documentation Standards

#### 1. Migrated from Redis to Valkey

**Change:**
- Replaced Redis with Valkey in `docker-compose.yml`
- Valkey is an open-source, drop-in replacement for Redis
- **Zero code changes required** - same API, same functionality

**Files Modified:**
- `docker-compose.yml`

**Docker Compose Configuration:**
```yaml
services:
  valkey:
    image: valkey/valkey:latest
    container_name: valkey_queue
    ports:
      - "6379:6379"
    volumes:
      - valkey_data:/data
    restart: unless-stopped

volumes:
  valkey_data:
```

---

#### 2. Fixed Directory Naming Convention

**Change:**
- Renamed `queue/` → `workers/` → `queues/` to match documentation
- Final structure aligns with the reference documentation

**Directory Structure:**
```
rag_queue/
├── client/
│   ├── __init__.py
│   └── rq_client.py
├── queues/           # ← Correct naming
│   ├── __init__.py
│   └── worker.py
├── server.py
├── main.py
└── docker-compose.yml
```

---

#### 3. Simplified Queue Configuration

**Before:**
```python
# Complex queue naming with explicit paths
QUEUE_NAME = "rag_queue.workers.worker"
queue = Queue(name=QUEUE_NAME, connection=Redis(...))

# String-based enqueue
job = queue.enqueue("workers.worker.process_query", query)
```

**After:**
```python
# Simple default queue (matches documentation)
redis_connection = Redis(host="localhost", port=6379)
queue = Queue(connection=redis_connection)

# Function reference enqueue (cleaner)
job = queue.enqueue(process_query, query)
```

**Why This Is Better:**
- Uses RQ's default queue (no custom naming needed)
- Worker command simplified: `rq worker` instead of `rq worker rag_queue.workers.worker`
- Function references are type-safe and IDE-friendly
- Matches industry best practices from documentation

**Files Modified:**
- `client/rq_client.py`
- `server.py`

---

#### 4. Enhanced API Routes

**Updated Routes:**

```python
# Route 1: Submit Query (Producer)
@app.post("/chat")
def chat(query: str = Query(..., description="Your question")):
    job = queue.enqueue(process_query, query)
    return {
        "message": "Your query has been queued for processing ⏳",
        "job_id": job.id,
        "status": "queued",
        "tip": f"Check your result at: GET /result/{job.id}"
    }

# Route 2: Fetch Result (Consumer)
@app.get("/result/{job_id}")
def get_result(job_id: str):
    from rq.job import Job
    from client.rq_client import redis_connection
    
    try:
        job = Job.fetch(job_id, connection=redis_connection)
    except Exception:
        return {"error": "Job not found. Check your Job ID."}
    
    if job.is_finished:
        return {
            "job_id": job_id,
            "status": "finished ✅",
            "result": job.result
        }
    elif job.is_failed:
        return {
            "job_id": job_id,
            "status": "failed ❌",
            "error": str(job.exc_info)
        }
    else:
        return {
            "job_id": job_id,
            "status": job.get_status(),
            "message": "Still processing... try again in a few seconds ⏳"
        }
```

**Changes:**
- Route path: `/job-status` → `/result/{job_id}` (RESTful pattern)
- Better status messages with emojis for clarity
- Proper error handling with try/except
- Informative response format

**Files Modified:**
- `server.py`

---

#### 5. Improved main.py Entry Point

**Updated:**
```python
import uvicorn
from dotenv import load_dotenv

# Load environment variables (.env file) BEFORE importing the app
# This ensures OPENAI_API_KEY is available everywhere
load_dotenv()

from server import app

def main():
    """Start the FastAPI server using Uvicorn."""
    uvicorn.run(
        app,
        host="0.0.0.0",   # Accept connections from any IP
        port=8000         # Server runs on http://localhost:8000
    )

if __name__ == "__main__":
    main()
```

**Why:**
- Loads environment variables BEFORE app import (critical for worker)
- Clean entry point with proper documentation
- Matches production-ready patterns

**Files Modified:**
- `main.py`

---

### Bug Fixes from Initial Implementation

#### 1. Fixed ImportError: Relative Import Issue

**Problem:**
```
ImportError: attempted relative import with no known parent package
```

**Root Cause:**
- Used relative imports (`from .client...`) in script run directly
- Relative imports only work when file is imported as module

**Solution:**
- Changed to absolute imports
- Works correctly when run as script or module

---

#### 2. Fixed Module Name Conflict

**Problem:**
```
ModuleNotFoundError: No module named 'queue.worker'; 'queue' is not a package
```

**Root Cause:**
- Local directory named `queue/` conflicted with Python's built-in `queue` module
- Python prioritized built-in module over local directory

**Solutions Attempted:**
1. ❌ Used `importlib` to explicitly load module (too complex)
2. ❌ Renamed to `workers/` (didn't match documentation)
3. ✅ Renamed to `queues/` + simplified queue configuration (perfect!)

---

### Running Instructions

The project now runs successfully with three components:

#### Terminal 1: Valkey (Message Broker)
```bash
cd /Users/work/Desktop/rag_queue
docker compose up -d
```
**Status:** ✅ Running on port 6379

#### Terminal 2: RQ Worker (Consumer)
```bash
cd /Users/work/Desktop/rag_queue
source .venv/bin/activate
rq worker --with-scheduler
```
**Status:** ✅ Listening on **default** queue

#### Terminal 3: FastAPI Server (Producer)
```bash
cd /Users/work/Desktop/rag_queue
source .venv/bin/activate
python -m main
```
**Status:** ✅ Running on http://0.0.0.0:8000

---

### Testing the System

#### Using cURL

**Submit a query:**
```bash
curl -X POST "http://localhost:8000/chat?query=What%20is%20Kubernetes"
```

**Response:**
```json
{
  "message": "Your query has been queued for processing ⏳",
  "job_id": "abc-123-xyz",
  "status": "queued",
  "tip": "Check your result at: GET /result/abc-123-xyz"
}
```

**Check result:**
```bash
curl "http://localhost:8000/result/abc-123-xyz"
```

**Response:**
```json
{
  "job_id": "abc-123-xyz",
  "status": "finished ✅",
  "result": "Kubernetes is an open-source container orchestration platform..."
}
```

#### Using FastAPI Docs

Visit: http://localhost:8000/docs

---

### Architecture Summary

```
User → POST /chat → FastAPI Server → queue.enqueue() → Valkey Queue
                                                             ↓
                                                       RQ Worker picks job
                                                             ↓
                                                    process_query() executes
                                                             ↓
                                                    Result stored in Valkey
                                                             ↓
User → GET /result/{job_id} → FastAPI reads from Valkey → Returns result
```

---

### Key Improvements

✅ **Valkey instead of Redis** - Open source, no licensing concerns  
✅ **Simplified queue naming** - Uses default queue pattern  
✅ **Function references** - Type-safe, not string-based  
✅ **RESTful routes** - `/result/{job_id}` instead of `/job-status?job_id=...`  
✅ **Better error handling** - Try/except with informative messages  
✅ **Documentation aligned** - Code matches reference documentation exactly  
✅ **No module conflicts** - `queues/` directory name doesn't clash with built-ins

---

### Summary

All code has been refactored to match the reference documentation. The system now follows industry best practices for async queue-based architectures using FastAPI, Python RQ, and Valkey.

**System Status:** ✅ Fully Operational

---

## macOS Fork Safety Issue - CRITICAL FIX (March 5, 2026)

### Problem: Worker Crashes on macOS

**Symptoms:**
```
Exception Type: EXC_CRASH (SIGABRT)
Termination Reason: Namespace OBJC, Code 1
Application Specific Information: crashed on child side of fork pre-exec
```

**Root Cause:**
- Python's RQ worker uses `multiprocessing.fork()` to create child processes
- After fork, Python imports modules that call macOS Objective-C APIs (system proxy detection via `_scproxy`)
- macOS Objective-C runtime enforces fork-safety and kills processes that violate this

**Technical Details:**
- Stack trace shows: `SCDynamicStoreCopyProxiesWithOptions` → `get_proxies` in `_scproxy.cpython-314-darwin.so`
- This happens when urllib tries to auto-detect system HTTP proxy settings
- macOS High Sierra+ has strict fork safety protections

### Solutions Implemented

**Solution 1: Use Startup Script (Recommended)**
```bash
./start_worker_safe.sh
```

This sets:
- `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` - Disables macOS fork safety check
- `NO_PROXY="*"` - Prevents proxy detection

**Solution 2: Manual Environment Variables**
```bash
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export NO_PROXY="*"
rq worker --with-scheduler
```

**Solution 3: Code-Level Fix**
Worker now imports `worker_config.py` which sets multiprocessing to use `spawn` instead of `fork`.

### Files Modified
- `queues/worker_config.py` - NEW: Sets multiprocessing spawn mode
- `queues/worker.py` - Updated to import worker_config first
- `start_worker.sh` - NEW: Basic startup script
- `start_worker_safe.sh` - NEW: Recommended startup with all safety flags

### References
- [Python Issue 33725](https://bugs.python.org/issue33725)
- [Apple Technical Note TN2083](https://developer.apple.com/library/archive/technotes/tn2083)
- macOS fork safety: `man 2 fork` (see CAVEATS section)

