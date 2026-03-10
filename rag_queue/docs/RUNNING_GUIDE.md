# 🚀 RAG Queue — Running Guide

> **Async RAG system** built with FastAPI + Redis Queue + Qdrant + OpenAI.
> Submit questions about your documents via API → get AI-powered answers asynchronously.

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Quick Start (3 Terminals)](#-quick-start-3-terminals)
- [Step-by-Step Setup](#-step-by-step-setup)
- [API Usage & Testing](#-api-usage--testing)
- [Architecture](#-architecture)
- [Stopping Everything](#-stopping-everything)
- [Troubleshooting](#-troubleshooting)

---

## ✅ Prerequisites

Make sure these are installed on your system before proceeding:

| Tool | Version | Check Command | Install |
|------|---------|---------------|---------|
| **Python** | 3.9+ | `python3 --version` | [python.org](https://python.org) |
| **Docker** | Latest | `docker --version` | [docker.com](https://docker.com) |
| **Docker Compose** | v2+ | `docker compose version` | Bundled with Docker Desktop |
| **OpenAI API Key** | — | — | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |

---

## ⚡ Quick Start (3 Terminals)

If you've already done the setup once, here's the fast path:

```bash
# ──── Terminal 1: Start Redis/Valkey + Qdrant ────
docker compose up -d

# ──── Terminal 2: Start FastAPI Server ────
source .venv/bin/activate
python main.py

# ──── Terminal 3: Start RQ Worker ────
source .venv/bin/activate
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES rq worker --with-scheduler
```

Server will be live at **http://localhost:8000** 🎉

---

## 🔧 Step-by-Step Setup

### Step 1 — Clone & Navigate

```bash
cd /path/to/rag_queue
```

### Step 2 — Create Virtual Environment

```bash
python3 -m venv .venv
```

### Step 3 — Activate Virtual Environment

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

> You should see `(.venv)` in your terminal prompt.

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏳ This installs ~100 packages (FastAPI, OpenAI, LangChain, RQ, Qdrant, etc.). Takes 3-5 min.

### Step 5 — Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

> ⚠️ **Never commit `.env` to git.** Add it to `.gitignore`.

### Step 6 — Start Docker Services (Valkey + Qdrant)

**Start Valkey (Redis-compatible) container:**

```bash
docker compose up -d
```

**Start Qdrant (if not already running):**

```bash
docker run -d --name qdrant \
  -p 6333:6333 \
  qdrant/qdrant:latest
```

**Verify both are running:**

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Expected output:
```
NAMES             STATUS       PORTS
valkey_queue      Up ...       0.0.0.0:6379->6379/tcp
qdrant            Up ...       0.0.0.0:6333->6333/tcp
```

**Verify Redis connectivity:**

```bash
docker exec -it valkey_queue redis-cli ping
# Expected: PONG
```

**Verify Qdrant dashboard:**

Open [http://localhost:6333/dashboard](http://localhost:6333/dashboard) in your browser.

> ⚠️ **Important:** The Qdrant collection `learning-rag` must exist with pre-indexed document embeddings. If it doesn't, you need to run your document indexing pipeline first.

### Step 7 — Start the FastAPI Server (Terminal 1)

```bash
source .venv/bin/activate
python main.py
```

Expected output:
```
INFO:     Started server process [PID]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Verify:** Open [http://localhost:8000](http://localhost:8000) — you should see:
```json
{"status": "Server is up and running"}
```

📖 **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

### Step 8 — Start the RQ Worker (Terminal 2)

Open a **new terminal**, then:

```bash
source .venv/bin/activate
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES rq worker --with-scheduler
```

> The `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` flag is **required on macOS** to prevent fork safety crashes.

**Alternative:** Use the provided shell script:

```bash
./start_worker_safe.sh
```

Expected output:
```
Worker abc123: started with PID 12345, version 2.6.0
*** Listening on default...
```

> ✅ **Both terminals must stay open.** The server and worker run as foreground processes.

---

## 🧪 API Usage & Testing

### Endpoint Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/chat?user_query=...` | Submit a question (returns Job ID) |
| `GET` | `/result/{job_id}` | Get result by Job ID |

---

### Test 1 — Health Check

```bash
curl http://localhost:8000/
```

```json
{"status": "Server is up and running"}
```

---

### Test 2 — Submit a Query

```bash
curl -X POST "http://localhost:8000/chat?user_query=What+is+JavaScript"
```

```json
{
  "message": "Your query has been queued for processing ⏳",
  "job_id": "27a4429d-9328-4ee7-a7c8-c6869eac04ce",
  "status": "queued",
  "tip": "Check your result at: GET /result/27a4429d-9328-4ee7-a7c8-c6869eac04ce"
}
```

> 📝 **Copy the `job_id`** — you'll need it to fetch the result.

---

### Test 3 — Fetch the Result

Wait 5-10 seconds for the worker to process, then:

```bash
curl http://localhost:8000/result/27a4429d-9328-4ee7-a7c8-c6869eac04ce
```

**If still processing:**
```json
{
  "job_id": "27a4429d-...",
  "status": "started",
  "message": "Still processing... try again in a few seconds ⏳"
}
```

**When finished:**
```json
{
  "job_id": "27a4429d-...",
  "status": "finished ✅",
  "result": "JavaScript is a programming language commonly used... (page 12)"
}
```

---

### Test 4 — Invalid Job ID

```bash
curl http://localhost:8000/result/fake-id-12345
```

```json
{"error": "Job not found. Check your Job ID."}
```

---

### Using Swagger UI (Browser)

1. Open [http://localhost:8000/docs](http://localhost:8000/docs)
2. Click **POST /chat** → **Try it out**
3. Enter your question in the `user_query` field
4. Click **Execute**
5. Copy the `job_id` from the response
6. Click **GET /result/{job_id}** → **Try it out**
7. Paste the `job_id` → **Execute**
8. See your AI-generated answer!

---

### Full Test Script (Python)

Save as `test_api.py` and run with `python test_api.py`:

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Health check
print("1️⃣  Health Check...")
r = requests.get(f"{BASE_URL}/")
print(f"   {r.json()}\n")

# 2. Submit query
print("2️⃣  Submitting query...")
r = requests.post(f"{BASE_URL}/chat", params={"user_query": "What is HTML?"})
data = r.json()
job_id = data["job_id"]
print(f"   Job ID: {job_id}")
print(f"   Status: {data['status']}\n")

# 3. Poll for result
print("3️⃣  Waiting for result...")
for i in range(20):
    time.sleep(2)
    r = requests.get(f"{BASE_URL}/result/{job_id}")
    result = r.json()
    status = result.get("status", "")
    print(f"   [{i+1}] Status: {status}")
    
    if "finished" in status:
        print(f"\n✅ Answer:\n{result['result']}")
        break
    elif "failed" in status:
        print(f"\n❌ Error:\n{result.get('error')}")
        break
else:
    print("\n⏰ Timeout — job is still processing.")
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      YOUR MACHINE                            │
│                                                              │
│  Terminal 1              Terminal 2           Docker          │
│  ┌────────────────┐     ┌──────────────┐    ┌────────────┐  │
│  │  FastAPI Server │     │  RQ Worker   │    │  Valkey    │  │
│  │  :8000          │     │              │    │  :6379     │  │
│  │                 │     │              │    ├────────────┤  │
│  │ POST /chat ─────┼──►  │              │    │  Qdrant    │  │
│  │ GET /result ◄───┼──── │ process_query│◄──►│  :6333     │  │
│  └────────────────┘     └──────────────┘    └────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     ┌────────────────┐
                     │   OpenAI API   │
                     │  GPT-4o +      │
                     │  Embeddings    │
                     └────────────────┘
```

### Request Flow

```
User sends query ──► FastAPI receives it
                      │
                      ├── Enqueues job to Redis Queue
                      └── Returns job_id immediately (non-blocking)
                                │
                    RQ Worker picks up job
                      │
                      ├── 1. Embeds query (OpenAI Embeddings)
                      ├── 2. Searches Qdrant vector DB
                      ├── 3. Builds context from results
                      ├── 4. Sends context + query to GPT-4o
                      └── 5. Stores answer in Redis
                                │
User polls GET /result/{id} ──► Returns the answer ✅
```

---

## 🛑 Stopping Everything

```bash
# 1. Stop the RQ Worker (Terminal 2)
#    Press Ctrl+C — waits for current job to finish

# 2. Stop the FastAPI Server (Terminal 1)
#    Press Ctrl+C

# 3. Stop Docker containers
docker compose down          # Stop containers, keep data
docker compose down -v       # Stop containers + DELETE data
```

---

## 🔥 Troubleshooting

### Connection Refused on :8000

```bash
# Check if server is running
lsof -i :8000

# If port is occupied, kill the process
kill -9 $(lsof -ti :8000)

# Restart the server
python main.py
```

### Jobs Stay "queued" Forever

The RQ worker is **not running** or **crashed**.

```bash
# Check if worker is running — look at Terminal 2
# If crashed, restart:
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES rq worker --with-scheduler
```

### Redis Connection Error

```bash
# Check if Valkey container is running
docker ps | grep valkey

# If not running, start it
docker compose up -d

# Test connectivity
docker exec -it valkey_queue redis-cli ping
# Expected: PONG
```

### OpenAI API Key Error

```bash
# Verify your key is loaded
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key loaded:', bool(os.getenv('OPENAI_API_KEY')))"
```

Common issues:
- ❌ Extra spaces around `=` in `.env` → use `OPENAI_API_KEY=sk-proj-...`
- ❌ Key wrapped in quotes → use raw value, no quotes
- ❌ Key revoked/expired → generate a new one at [platform.openai.com](https://platform.openai.com/api-keys)

### Qdrant Collection Not Found

```bash
# Check if collection exists
curl http://localhost:6333/collections

# If "learning-rag" is missing, you need to run your
# document indexing pipeline to create embeddings first.
```

### macOS Fork Safety Crash

If the worker crashes with `objc[PID]: +[__NSCFConstantString initialize] may have been in progress...`:

```bash
# Always set this env var before starting the worker on macOS
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
rq worker --with-scheduler

# Or use the provided script
./start_worker_safe.sh
```

### Import Errors / Module Not Found

```bash
# Make sure virtualenv is activated — look for (.venv) in prompt
source .venv/bin/activate

# Reinstall all dependencies
pip install -r requirements.txt
```

### Qdrant Version Mismatch Warning

If you see: `Qdrant client version X is incompatible with server version Y`:

```bash
# Update the client to match server
pip install --upgrade qdrant-client
```

---

## 📁 Project Structure

```
rag_queue/
├── main.py                  # Entry point — starts Uvicorn server
├── server.py                # FastAPI app — defines API routes
├── .env                     # API keys (⚠️ never commit)
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Valkey (Redis) container config
├── start_worker.sh          # Worker startup script
├── start_worker_safe.sh     # Worker startup (macOS safe)
│
├── client/
│   ├── __init__.py
│   └── rq_client.py         # Redis connection + Queue setup
│
└── queues/
    ├── __init__.py
    ├── worker.py             # RAG processing logic (process_query)
    └── worker_config.py      # macOS multiprocessing config
```

---

**Happy querying! 🎉**
