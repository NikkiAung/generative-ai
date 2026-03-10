# Redis Job Storage — How RQ Stores Jobs in Redis

> A deep-dive into the internal Redis data structures used by **RQ (Redis Queue)** in the RAG Queue project.

---

## Table of Contents
- [Overview](#overview)
- [Redis Key Namespace Map](#redis-key-namespace-map)
- [Job Lifecycle in Redis](#job-lifecycle-in-redis)
- [Data Structures Diagram](#data-structures-diagram)
- [Key-by-Key Breakdown](#key-by-key-breakdown)
- [Full Example Walkthrough](#full-example-walkthrough)
- [Memory & TTL Behavior](#memory--ttl-behavior)
- [Redis CLI Cheat Sheet](#redis-cli-cheat-sheet)

---

## Overview

When a user calls `POST /chat?query="What is RAG?"`, the FastAPI server pushes a job into Redis via `queue.enqueue(process_query, user_query)`. Under the hood, **RQ uses several Redis data structures** — Hashes, Lists, Sets, and Sorted Sets — to manage the complete lifecycle of every job.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         REDIS INSTANCE (port 6379)                  │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                     QUEUE REGISTRY                              │ │
│  │                                                                  │ │
│  │   rq:queues  (SET)                                              │ │
│  │      └── "rq:queue:default"                                     │ │
│  │                                                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                     JOB QUEUE (FIFO)                            │ │
│  │                                                                  │ │
│  │   rq:queue:default  (LIST)                                      │ │
│  │      ├── job_id_001                                             │ │
│  │      ├── job_id_002                                             │ │
│  │      └── job_id_003                                             │ │
│  │                                                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    JOB DATA (per job)                           │ │
│  │                                                                  │ │
│  │   rq:job:<job_id>  (HASH)                                      │ │
│  │      ├── data          → pickled function + args                │ │
│  │      ├── status        → queued | started | finished | failed   │ │
│  │      ├── origin        → "default"                              │ │
│  │      ├── created_at    → "2026-03-06T00:05:26Z"                │ │
│  │      ├── enqueued_at   → "2026-03-06T00:05:26Z"                │ │
│  │      ├── started_at    → "2026-03-06T00:05:27Z"                │ │
│  │      ├── ended_at      → "2026-03-06T00:05:35Z"                │ │
│  │      ├── result        → pickled return value                   │ │
│  │      ├── exc_info      → traceback (if failed)                  │ │
│  │      ├── timeout       → 180                                    │ │
│  │      └── worker_name   → "worker-abc123"                        │ │
│  │                                                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                   STATUS REGISTRIES                             │ │
│  │                                                                  │ │
│  │   rq:started:default    (SORTED SET)  → currently executing     │ │
│  │   rq:finished:default   (SORTED SET)  → completed successfully  │ │
│  │   rq:failed:default     (SORTED SET)  → jobs that errored       │ │
│  │   rq:deferred:default   (SORTED SET)  → scheduled for later     │ │
│  │   rq:canceled:default   (SORTED SET)  → canceled jobs           │ │
│  │                                                                  │ │
│  │   Score = UNIX timestamp of state transition                    │ │
│  │                                                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                   WORKER REGISTRY                               │ │
│  │                                                                  │ │
│  │   rq:workers  (SET)                                             │ │
│  │      ├── "rq:worker:worker-abc123"                              │ │
│  │      └── "rq:worker:worker-def456"                              │ │
│  │                                                                  │ │
│  │   rq:worker:<name>  (HASH)                                     │ │
│  │      ├── hostname       → "MacBook-Pro.local"                   │ │
│  │      ├── pid            → 42731                                 │ │
│  │      ├── state          → "busy" | "idle"                       │ │
│  │      ├── current_job    → "<job_id>" or ""                      │ │
│  │      ├── queues         → "default"                             │ │
│  │      └── birth_date     → "2026-03-06T00:00:00Z"               │ │
│  │                                                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Redis Key Namespace Map

All RQ keys live under the `rq:` prefix. Here is the complete namespace:

```
rq:
├── queues                              ← SET of all registered queues
│
├── queue:default                       ← LIST (FIFO) of pending job IDs
│
├── job:<uuid>                          ← HASH with full job payload & metadata
│   ├── job:abc12345-...
│   ├── job:def67890-...
│   └── job:ghi11223-...
│
├── started:default                     ← SORTED SET (score = timestamp)
├── finished:default                    ← SORTED SET (score = timestamp)
├── failed:default                      ← SORTED SET (score = timestamp)
├── deferred:default                    ← SORTED SET (score = timestamp)
├── canceled:default                    ← SORTED SET (score = timestamp)
│
├── workers                             ← SET of active worker keys
├── worker:<worker-name>                ← HASH with worker info
│
└── clean_registries:default            ← STRING (lock for cleanup)
```

---

## Job Lifecycle in Redis

This diagram shows how a job moves through different Redis keys during its lifecycle:

```
                         ┌─────────────────────┐
                         │  queue.enqueue()     │
                         │  (FastAPI Server)    │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌──────────────┐ ┌────────────┐ ┌─────────────────┐
            │ HSET          │ │ LPUSH      │ │ SADD            │
            │ rq:job:<id>   │ │ rq:queue:  │ │ rq:queues       │
            │               │ │ default    │ │                 │
            │ status=queued │ │ <job_id>   │ │ "rq:queue:      │
            │ data=pickle(  │ │            │ │  default"       │
            │  process_query│ └──────┬─────┘ └─────────────────┘
            │  , args)      │        │
            └──────┬───────┘        │
                   │                │
                   │   ┌────────────┘
                   │   │
                   ▼   ▼
        ┌───────────────────────────────┐
        │  WORKER picks up job          │
        │                               │
        │  1. RPOP rq:queue:default     │   ◄── Pops job_id from right
        │  2. HSET rq:job:<id>          │       (FIFO order)
        │     status = "started"        │
        │  3. ZADD rq:started:default   │
        │     <timestamp> <job_id>      │
        └───────────────┬───────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
       ✅ SUCCESS              ❌ FAILURE
            │                       │
            ▼                       ▼
  ┌──────────────────┐    ┌──────────────────┐
  │ HSET rq:job:<id> │    │ HSET rq:job:<id> │
  │  status=finished │    │  status=failed   │
  │  result=pickle(  │    │  exc_info=       │
  │   "Based on      │    │   traceback      │
  │    page 42...")   │    │                  │
  │                  │    │                  │
  │ ZREM             │    │ ZREM             │
  │  rq:started:     │    │  rq:started:     │
  │  default         │    │  default         │
  │                  │    │                  │
  │ ZADD             │    │ ZADD             │
  │  rq:finished:    │    │  rq:failed:      │
  │  default         │    │  default         │
  │  <ts> <job_id>   │    │  <ts> <job_id>   │
  └──────────────────┘    └──────────────────┘
            │                       │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  Client polls result  │
            │  GET /result/<job_id> │
            │                       │
            │  Job.fetch(job_id,    │
            │    connection=redis)  │
            │                       │
            │  → HGETALL            │
            │    rq:job:<job_id>    │
            │                       │
            │  Returns:             │
            │    job.result         │
            │    job.status         │
            │    job.exc_info       │
            └───────────────────────┘
```

---

## Data Structures Diagram

### Per-Job Hash — `rq:job:<job_id>`

This is the **most important key** — it holds everything about a single job.

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  KEY:  rq:job:a1b2c3d4-e5f6-7890-abcd-ef1234567890                 │
│  TYPE: HASH                                                          │
│                                                                      │
│  ┌────────────────┬────────────────────────────────────────────────┐ │
│  │   Field        │   Value                                        │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ data           │ \x80\x05\x95... (pickled bytes)               │ │
│  │                │                                                │ │
│  │                │ Unpickled ──►                                  │ │
│  │                │ {                                              │ │
│  │                │   func: "queues.worker.process_query",        │ │
│  │                │   args: ("What is RAG?",),                    │ │
│  │                │   kwargs: {}                                   │ │
│  │                │ }                                              │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ status         │ "queued" → "started" → "finished" / "failed"  │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ origin         │ "default"  (queue name)                       │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ description    │ "queues.worker.process_query('What is RAG?')" │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ created_at     │ "2026-03-06T00:05:26.123456Z"                 │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ enqueued_at    │ "2026-03-06T00:05:26.124000Z"                 │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ started_at     │ "2026-03-06T00:05:27.500000Z"                 │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ ended_at       │ "2026-03-06T00:05:35.200000Z"                 │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ result         │ \x80\x05\x95... (pickled bytes)               │ │
│  │                │                                                │ │
│  │                │ Unpickled ──►                                  │ │
│  │                │ "Based on page 42, RAG stands for             │ │
│  │                │  Retrieval-Augmented Generation..."            │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ exc_info       │ "" (empty on success, traceback on failure)    │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ timeout        │ "180"  (seconds)                               │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ result_ttl     │ "-1"  (seconds, -1 = persist forever)         │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ worker_name    │ "worker-abc123.MacBook-Pro.42731"              │ │
│  ├────────────────┼────────────────────────────────────────────────┤ │
│  │ last_heartbeat │ "2026-03-06T00:05:34.900000Z"                 │ │
│  └────────────────┴────────────────────────────────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Queue List — `rq:queue:default`

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                    │
│  KEY:  rq:queue:default                                           │
│  TYPE: LIST (operates as FIFO queue)                              │
│                                                                    │
│  Push side (LPUSH)                            Pop side (RPOP)     │
│  ◄───────────────────────────────────────────────────────────►    │
│                                                                    │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐   │
│  │  job_id_005  │  job_id_004  │  job_id_003  │  job_id_001  │   │
│  │  (newest)    │              │              │  (oldest)    │   │
│  └──────────────┴──────────────┴──────────────┴──────────────┘   │
│                                                                    │
│  • New jobs pushed to LEFT  (LPUSH)                               │
│  • Worker pops from RIGHT   (RPOP / BRPOP)                       │
│  • Guarantees First-In-First-Out processing                       │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### Status Registries — Sorted Sets

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                    │
│  KEY:  rq:finished:default                                        │
│  TYPE: SORTED SET                                                 │
│                                                                    │
│  ┌─────────────────────────────┬──────────────────────────────┐   │
│  │  Member (Job ID)            │  Score (UNIX Timestamp)      │   │
│  ├─────────────────────────────┼──────────────────────────────┤   │
│  │  a1b2c3d4-...-567890       │  1772851535.200               │   │
│  │  f9e8d7c6-...-234567       │  1772851542.800               │   │
│  │  b3c4d5e6-...-890123       │  1772851558.100               │   │
│  └─────────────────────────────┴──────────────────────────────┘   │
│                                                                    │
│  Same structure applies to:                                        │
│    • rq:started:default                                           │
│    • rq:failed:default                                            │
│    • rq:deferred:default                                          │
│    • rq:canceled:default                                          │
│                                                                    │
│  The timestamp score enables:                                      │
│    • Time-based queries (find jobs from last hour)                │
│    • Cleanup of old entries by score range                        │
│    • Ordering by completion time                                  │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key-by-Key Breakdown

| Redis Key | Type | Purpose | When Created | When Removed |
|---|---|---|---|---|
| `rq:queues` | SET | Global registry of all queue names | First `enqueue()` | Never (persistent) |
| `rq:queue:default` | LIST | FIFO queue of pending job IDs | `enqueue()` adds | Worker `RPOP` removes |
| `rq:job:<id>` | HASH | Complete job data, args, result, status | `enqueue()` | After `result_ttl` expires |
| `rq:started:default` | SORTED SET | Jobs currently being processed | Worker picks job | Worker completes/fails job |
| `rq:finished:default` | SORTED SET | Successfully completed job IDs | Worker finishes job | Periodic cleanup |
| `rq:failed:default` | SORTED SET | Failed job IDs | Worker catches exception | Manual cleanup / requeue |
| `rq:deferred:default` | SORTED SET | Scheduled / deferred jobs | `enqueue_at()` | Scheduler moves to queue |
| `rq:canceled:default` | SORTED SET | Canceled job IDs | `job.cancel()` | Periodic cleanup |
| `rq:workers` | SET | Active worker registrations | Worker starts | Worker shuts down |
| `rq:worker:<name>` | HASH | Individual worker state & heartbeat | Worker starts | Worker shuts down |

---

## Full Example Walkthrough

Here's what happens in Redis step-by-step when a user asks a question:

### Step 1: User sends `POST /chat?query="What is RAG?"`

```
FastAPI calls: queue.enqueue(process_query, "What is RAG?")
```

**Redis commands executed by RQ:**

```redis
# 1. Register the queue (idempotent)
SADD rq:queues "rq:queue:default"

# 2. Create the job hash with all metadata
HSET rq:job:a1b2c3d4-e5f6-7890-abcd-ef1234567890
    "data"        "\x80\x05\x95..."           # pickle(process_query, ("What is RAG?",))
    "status"      "queued"
    "origin"      "default"
    "description" "queues.worker.process_query('What is RAG?')"
    "created_at"  "2026-03-06T00:05:26.123456Z"
    "enqueued_at" "2026-03-06T00:05:26.124000Z"
    "timeout"     "180"
    "result_ttl"  "-1"

# 3. Push job ID into the queue (FIFO - push left, pop right)
LPUSH rq:queue:default "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

**Redis state after Step 1:**
```
rq:queues              = {"rq:queue:default"}
rq:queue:default       = ["a1b2c3d4-...-567890"]
rq:job:a1b2c3d4-...    = {status: "queued", data: ..., ...}
```

---

### Step 2: Worker picks up the job

```
RQ Worker executes: BRPOP rq:queue:default (blocking pop)
```

**Redis commands:**

```redis
# 1. Pop job ID from queue (blocking, waits for jobs)
BRPOP rq:queue:default 0
# Returns: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# 2. Update job status to "started"
HSET rq:job:a1b2c3d4-...-567890
    "status"     "started"
    "started_at" "2026-03-06T00:05:27.500000Z"
    "worker_name" "worker-abc123"

# 3. Add to started registry
ZADD rq:started:default 1772851527.5 "a1b2c3d4-...-567890"

# 4. Update worker state
HSET rq:worker:worker-abc123
    "state"       "busy"
    "current_job" "a1b2c3d4-...-567890"
```

**Redis state after Step 2:**
```
rq:queue:default       = []                           ◄── Empty now
rq:started:default     = {a1b2c3d4-...: 1772851527}   ◄── Job is here
rq:job:a1b2c3d4-...    = {status: "started", ...}
```

---

### Step 3: Worker completes processing (success)

```
process_query() returns: "Based on page 42, RAG stands for..."
```

**Redis commands:**

```redis
# 1. Store the result in the job hash
HSET rq:job:a1b2c3d4-...-567890
    "status"   "finished"
    "result"   "\x80\x05\x95..."    # pickle("Based on page 42, RAG stands for...")
    "ended_at" "2026-03-06T00:05:35.200000Z"

# 2. Move from started → finished registry
ZREM rq:started:default "a1b2c3d4-...-567890"
ZADD rq:finished:default 1772851535.2 "a1b2c3d4-...-567890"

# 3. Update worker state back to idle
HSET rq:worker:worker-abc123
    "state"       "idle"
    "current_job" ""
```

**Redis state after Step 3:**
```
rq:queue:default       = []
rq:started:default     = {}                            ◄── Removed
rq:finished:default    = {a1b2c3d4-...: 1772851535}    ◄── Job is here
rq:job:a1b2c3d4-...    = {status: "finished", result: ..., ...}
```

---

### Step 4: Client polls `GET /result/a1b2c3d4-...`

```python
# server.py calls:
job = Job.fetch("a1b2c3d4-...", connection=redis_connection)
job.result  # → "Based on page 42, RAG stands for..."
```

**Redis commands:**

```redis
# Fetch the entire job hash
HGETALL rq:job:a1b2c3d4-e5f6-7890-abcd-ef1234567890
# Returns all fields: status, result, created_at, ended_at, etc.
```

---

## Memory & TTL Behavior

```
┌──────────────────────────────────────────────────────────────────┐
│                   JOB RESULT LIFECYCLE                            │
│                                                                    │
│  ┌──────────────┐                                                 │
│  │  result_ttl   │                                                 │
│  │  (seconds)    │                                                 │
│  └──────┬───────┘                                                 │
│         │                                                          │
│         ├── result_ttl = -1  (DEFAULT in this project)            │
│         │   └── Job hash persists in Redis FOREVER                │
│         │       ⚠️  Can cause memory growth over time             │
│         │                                                          │
│         ├── result_ttl = 0                                        │
│         │   └── Job hash deleted IMMEDIATELY after completion     │
│         │       └── Result cannot be fetched!                     │
│         │                                                          │
│         ├── result_ttl = 500                                      │
│         │   └── Job hash expires 500 seconds after completion     │
│         │       └── Redis EXPIRE command applied to key           │
│         │                                                          │
│         └── result_ttl = 86400  (recommended for production)      │
│             └── Job hash expires after 24 hours                   │
│                 └── Good balance of access & memory               │
│                                                                    │
│  ─────────────────────────────────────────────────────────────    │
│                                                                    │
│  MEMORY PER JOB (approximate):                                    │
│                                                                    │
│  ┌───────────────────────┬──────────────────────────────────┐     │
│  │ Component             │ Approximate Size                  │     │
│  ├───────────────────────┼──────────────────────────────────┤     │
│  │ Job metadata          │ ~500 bytes                        │     │
│  │ Pickled function+args │ ~200–500 bytes                    │     │
│  │ Pickled result        │ ~500–5000 bytes (varies w/ answer)│     │
│  │ Status registries     │ ~100 bytes per entry              │     │
│  ├───────────────────────┼──────────────────────────────────┤     │
│  │ TOTAL per job         │ ~1–6 KB                           │     │
│  └───────────────────────┴──────────────────────────────────┘     │
│                                                                    │
│  At 10,000 jobs → ~10–60 MB of Redis memory                      │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Redis CLI Cheat Sheet

Use these commands to inspect the job storage in your running Redis instance:

```bash
# Connect to Redis
redis-cli -p 6379

# ───── Queue Inspection ─────

# See all registered queues
SMEMBERS rq:queues

# Count pending jobs in the default queue
LLEN rq:queue:default

# List all pending job IDs
LRANGE rq:queue:default 0 -1

# ───── Job Inspection ─────

# Get all data for a specific job
HGETALL rq:job:<job_id>

# Get just the status of a job
HGET rq:job:<job_id> status

# Get the result of a job
HGET rq:job:<job_id> result

# ───── Registry Inspection ─────

# See currently running jobs
ZRANGE rq:started:default 0 -1

# See finished jobs (with timestamps)
ZRANGE rq:finished:default 0 -1 WITHSCORES

# See failed jobs
ZRANGE rq:failed:default 0 -1

# Count finished jobs
ZCARD rq:finished:default

# ───── Worker Inspection ─────

# See all active workers
SMEMBERS rq:workers

# Get worker details
HGETALL rq:worker:<worker-name>

# ───── Cleanup ─────

# Find all RQ keys
KEYS rq:*

# Count all RQ keys
DBSIZE
```

---

## Visual Summary — State Transitions

```
                    ┌─────────┐
                    │ ENQUEUE │
                    └────┬────┘
                         │
                         ▼
                ┌────────────────┐       Redis Keys Involved:
                │    QUEUED      │       • rq:job:<id>      (HASH created)
                │                │       • rq:queue:default (LIST, LPUSH)
                └────────┬───────┘
                         │
                    Worker RPOP
                         │
                         ▼
                ┌────────────────┐       Redis Keys Involved:
                │    STARTED     │       • rq:job:<id>      (status → started)
                │                │       • rq:queue:default (RPOP removes)
                │  Worker is     │       • rq:started:default (ZADD)
                │  processing... │
                └───┬────────┬──┘
                    │        │
              Success      Failure
                    │        │
                    ▼        ▼
          ┌──────────┐  ┌──────────┐
          │ FINISHED │  │  FAILED  │    Redis Keys Involved:
          │          │  │          │    • rq:job:<id>         (status updated)
          │ result   │  │ exc_info │    • rq:started:default  (ZREM)
          │ stored   │  │ stored   │    • rq:finished/failed  (ZADD)
          └──────────┘  └──────────┘
               │             │
               ▼             ▼
          ┌──────────┐  ┌──────────┐
          │  Client  │  │  Retry?  │
          │  Fetches │  │  Re-     │
          │  Result  │  │  enqueue │
          └──────────┘  └──────────┘
```

---

> **💡 Key Takeaway:** Redis in this project is not just a simple message broker — it serves as the **job store**, **status tracker**, **result backend**, and **worker registry**, all using native Redis data structures (Hashes, Lists, Sets, Sorted Sets) for maximum performance.
