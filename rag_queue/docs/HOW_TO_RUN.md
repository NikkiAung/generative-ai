# How to Run RAG Queue Project

## Table of Contents
- [Prerequisites](#prerequisites)
- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Testing the System](#testing-the-system)
- [Troubleshooting](#troubleshooting)
- [Stopping the Application](#stopping-the-application)
- [Development Workflow](#development-workflow)
- [Production Deployment](#production-deployment)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Prerequisites

### Required Software

Before running this project, ensure you have the following installed on your system:

#### 1. **Python 3.9 or Higher**

Check if Python is installed and verify the version:

**On macOS/Linux:**
Open Terminal and check Python version. If not installed, download from python.org or use a package manager.

**On Windows:**
Download Python installer from python.org and ensure "Add Python to PATH" is checked during installation.

#### 2. **pip (Python Package Manager)**

pip usually comes with Python installation. Verify it's available on your system.

#### 3. **Docker and Docker Compose**

Docker is required to run Redis/Valkey container.

**Installation:**
- **macOS**: Download Docker Desktop from docker.com
- **Windows**: Download Docker Desktop from docker.com
- **Linux**: Install Docker Engine and Docker Compose using your package manager

Verify Docker is installed and running by checking the version.

#### 4. **OpenAI API Key**

You need an active OpenAI account with API access.

**Steps to Get API Key:**
1. Visit platform.openai.com
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy and save the key securely (you'll only see it once)

**Important:** OpenAI API is a paid service. Ensure you have billing configured and understand the costs associated with GPT-4o and embedding models.

#### 5. **Qdrant Vector Database**

You need a running Qdrant instance with a pre-populated collection named `learning-rag`.

**Options:**
- Run Qdrant locally using Docker
- Use Qdrant Cloud (free tier available)
- Run Qdrant from source

**Docker Installation (Recommended):**
Start Qdrant container on port 6333. Verify it's running by accessing the web UI at localhost:6333/dashboard.

**Collection Setup:**
Before running the worker, ensure the `learning-rag` collection exists and contains document embeddings. This requires a separate indexing step where you:
1. Load your PDF documents
2. Split them into chunks
3. Generate embeddings using OpenAI
4. Store embeddings in Qdrant with metadata (page numbers, file locations)

---

## System Requirements

### Minimum Hardware Requirements

**For Development:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 1 GB free space
- Internet: Stable connection for API calls

**For Production:**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 10+ GB (depends on document volume)
- Network: Low-latency connection to OpenAI API

### Supported Operating Systems

- macOS 10.15+
- Ubuntu 20.04+
- Windows 10/11 with WSL2 (for Docker)
- Any Linux distribution with Docker support

---

## Installation Steps

### Step 1: Clone or Download the Project

Navigate to the directory where you want to set up the project. If you have the project as a ZIP file, extract it.

### Step 2: Navigate to Project Directory

Change into the project directory after extracting or cloning.

### Step 3: Create a Virtual Environment

Creating a virtual environment isolates project dependencies from system Python packages.

**On macOS/Linux:**
Create a virtual environment using the venv module.

**On Windows:**
Use the python command with venv module to create isolated environment.

**Why Virtual Environment?**
- Prevents dependency conflicts
- Makes project portable
- Easier to manage package versions

### Step 4: Activate Virtual Environment

**On macOS/Linux:**
Activate the virtual environment using the source command.

**On Windows:**
Run the activation script from the Scripts folder.

**Verification:**
After activation, your terminal prompt should show the environment name in parentheses.

### Step 5: Install Python Dependencies

Install all required Python packages listed in requirements.txt. This will download and install approximately 90+ packages including FastAPI, OpenAI, LangChain, RQ, Redis client, Qdrant client, and their dependencies.

**This may take 3-5 minutes** depending on your internet connection.

**Verification:**
Check that packages are installed by verifying specific package installations.

### Step 6: Start Docker Services

Start Redis/Valkey container using Docker Compose. The compose file defines a Valkey service (Redis-compatible) that will run in the background.

**Verification:**
Check that the container is running and healthy.

Access Redis CLI to verify connectivity. You should see a PONG response if Redis is working correctly.

### Step 7: Verify Qdrant is Running

Ensure your Qdrant instance is accessible. If running locally via Docker, verify the container is running. Check the web interface by opening localhost:6333/dashboard in your browser.

**Verify Collection Exists:**
Use Qdrant's REST API to list collections and confirm `learning-rag` exists with embeddings.

If the collection doesn't exist, you need to run your document indexing pipeline first.

---

## Environment Configuration

### Step 1: Create .env File

Create a file named `.env` in the project root directory. This file stores sensitive configuration and should **never** be committed to version control.

### Step 2: Add Required Environment Variables

Add the following variables to your .env file:

**Essential Variables:**

OPENAI_API_KEY - Your OpenAI API key from platform.openai.com

**Optional Variables (with defaults):**

REDIS_HOST - Redis server address (default: localhost)
REDIS_PORT - Redis server port (default: 6379)
QDRANT_URL - Qdrant server URL (default: http://localhost:6333)
QDRANT_COLLECTION - Collection name (default: learning-rag)

**Example .env File:**

Create a template with your actual API key and customize other settings as needed.

### Step 3: Verify Environment Loading

The application uses python-dotenv to automatically load these variables. Verify that environment variables are loaded by running a quick Python test.

---

## Running the Application

### Architecture Recap

The application consists of **three components** that must run simultaneously:

1. **Redis/Valkey** (Message Broker) - Already running via Docker
2. **FastAPI Server** (API Layer) - Receives requests and enqueues jobs
3. **RQ Worker** (Processing Layer) - Processes queued jobs

### Running Components

#### Component 1: Redis/Valkey (Already Running)

If you followed the installation steps, this should already be running. Verify with Docker commands.

---

#### Component 2: Start FastAPI Server

Open a **new terminal window** (keep it separate from the worker). Navigate to the project directory, activate the virtual environment, then start the FastAPI server.

**What happens:**
- Uvicorn ASGI server starts
- FastAPI application loads
- Server binds to port 8000
- API documentation becomes available

**Expected Output:**
You should see log messages indicating the server has started successfully.

**Verification:**
Test the health endpoint by accessing localhost:8000 in your browser or using curl. You should see a JSON response indicating the server is running.

**Access API Documentation:**
FastAPI automatically generates interactive documentation:
- Swagger UI: localhost:8000/docs
- ReDoc: localhost:8000/redoc

**Keep this terminal running** - do not close it.

---

#### Component 3: Start RQ Worker

Open **another new terminal window** (you should now have 2 terminals open). Navigate to the project directory and activate the virtual environment.

**Start the worker using RQ's command-line tool:**

Run the worker on the queue with function imports from the worker module.

**Important Parameters Explained:**

- **Worker process that monitors the queue**
- **Queue name (must match the queue defined in rq_client.py)**
- **Python module path where worker functions are defined**

**Expected Output:**
You should see messages indicating the worker has started and is listening for jobs.

**Verification:**
The worker should display log messages showing it's connected to Redis and waiting for jobs.

**Keep this terminal running** - the worker needs to stay active to process jobs.

---

### System Status Check

At this point, you should have **three processes running**:

1. **Docker container** with Redis/Valkey (background daemon)
2. **Terminal 1**: FastAPI server on port 8000
3. **Terminal 2**: RQ worker listening to the queue

**Visual Representation:**

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR COMPUTER                        │
│                                                         │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Terminal 1    │  │  Terminal 2  │  │  Docker   │ │
│  │  FastAPI Server │  │  RQ Worker   │  │  Valkey   │ │
│  │  Port: 8000     │  │  Queue: rag  │  │  Port:    │ │
│  │                 │  │              │  │  6379     │ │
│  └─────────────────┘  └──────────────┘  └───────────┘ │
│           │                   │                │        │
│           └───────────────────┴────────────────┘        │
│                  All Connected via Redis                │
└─────────────────────────────────────────────────────────┘
```

---

## Testing the System

### Test 1: Health Check

Verify the API server is responsive by testing the root endpoint.

**Methods:**

**Browser:** Open localhost:8000 in your web browser

**curl command:** Use curl to send a GET request to the health endpoint

**Python requests:** Run a quick Python script to verify connectivity

**Expected Response:**
JSON object indicating the server is up and running.

---

### Test 2: Submit a Query

Test the chat endpoint by submitting a question.

**Using curl:**

Send a POST request with your query as a parameter.

**Using Python:**

Write a small Python script to interact with the API.

**Using API Documentation:**

1. Open localhost:8000/docs in browser
2. Click on POST /chat endpoint
3. Click "Try it out"
4. Enter a query in the query field
5. Click "Execute"

**Expected Response:**

JSON object with:
- status: "queued"
- job_id: A unique identifier (UUID format)

**Example Response:**
Status message with generated job identifier for tracking.

**Save the job_id** - you'll need it to retrieve results.

---

### Test 3: Check Job Status and Retrieve Results

Use the job_id from the previous step to fetch results.

**Using curl:**

Send a GET request to the job status endpoint with your job ID.

**Using Python:**

Create a script to poll for results until the job completes.

**Important Notes:**

**Processing Time:**
- Jobs typically take 3-15 seconds to process
- Time depends on query complexity and OpenAI API response time

**Job Status:**
- If job is still processing, return_value will be None
- Once complete, return_value contains the AI-generated answer

**Expected Response (when complete):**

JSON result with the answer including page number citations from the source documents.

---

### Test 4: View Worker Logs

Switch to the **Terminal 2** (where RQ worker is running).

**What to observe:**
- "Searching chunks" message with your query
- OpenAI API calls being made
- "Bot:" message with the generated response
- Job completion status

This confirms the worker is processing jobs correctly.

---

### End-to-End Test Flow Diagram

```
1. Client sends query
   │
   ▼
2. FastAPI receives request
   ├─► Validates query
   ├─► Creates job
   ├─► Enqueues to Redis
   └─► Returns job_id immediately
   │
   ▼
3. Worker picks up job
   ├─► Searches Qdrant
   ├─► Calls OpenAI
   └─► Stores result
   │
   ▼
4. Client polls with job_id
   │
   ▼
5. FastAPI returns result
   │
   ▼
6. Client receives answer
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Connection refused" when accessing API

**Symptoms:**
Unable to connect to localhost:8000

**Possible Causes:**
1. FastAPI server is not running
2. Server crashed during startup
3. Port 8000 is already in use

**Solutions:**

**Check if server is running:**
Look for the FastAPI terminal window and verify it's active.

**Check port availability:**
Use system commands to check if port 8000 is in use by another application.

**Try a different port:**
If port 8000 is occupied, start the server on a different port by modifying the main.py file or using command-line arguments.

---

#### Issue 2: Jobs never complete / Worker not processing

**Symptoms:**
Job stays in "queued" state indefinitely or return_value is always None.

**Possible Causes:**
1. RQ worker is not running
2. Worker crashed
3. Queue name mismatch
4. Redis connection issue

**Solutions:**

**Verify worker is running:**
Check the Terminal 2 window for worker logs.

**Check queue name:**
Ensure the queue name in rq_client.py matches the one used in the worker command.

**Restart worker:**
Stop the worker process and start it again with the correct parameters.

**Check Redis connection:**
Verify Redis is accessible and the worker can connect.

---

#### Issue 3: OpenAI API Errors

**Symptoms:**
Worker logs show authentication errors or rate limit errors.

**Common Errors:**

**Authentication Error:**
"Invalid API key" or "Unauthorized"

**Solution:**
- Verify OPENAI_API_KEY in .env file is correct
- Ensure no extra spaces or quotes around the key
- Check the key hasn't been revoked

**Rate Limit Error:**
"Rate limit exceeded"

**Solution:**
- You're making too many requests
- Wait a few minutes before trying again
- Consider upgrading your OpenAI plan
- Reduce concurrent workers

**Quota Exceeded:**
"You exceeded your current quota"

**Solution:**
- Add billing information to your OpenAI account
- Check your usage limits at platform.openai.com/usage
- Top up your account balance

---

#### Issue 4: Qdrant Connection Error

**Symptoms:**
Worker fails with "Connection refused" to Qdrant or "Collection not found"

**Solutions:**

**Verify Qdrant is running:**
Check if the Qdrant container or service is active.

**Check collection exists:**
Use Qdrant API or dashboard to verify the collection.

**Ensure correct URL:**
Verify QDRANT_URL in environment matches your Qdrant instance.

**Create collection if missing:**
You need to run your document indexing pipeline to create embeddings before queries work.

---

#### Issue 5: Redis Connection Error

**Symptoms:**
"Error connecting to Redis" or "Connection refused to localhost:6379"

**Solutions:**

**Verify Docker container is running:**
Check if the Valkey container is active.

**Restart Redis container:**
Stop and restart the Docker Compose services.

**Check port binding:**
Ensure port 6379 is not blocked by firewall.

---

#### Issue 6: Import Errors or Module Not Found

**Symptoms:**
Python throws ModuleNotFoundError when starting server or worker.

**Common Causes:**
1. Virtual environment not activated
2. Dependencies not installed
3. Wrong Python version

**Solutions:**

**Activate virtual environment:**
Ensure you activated the venv before running commands.

**Reinstall dependencies:**
Update pip and reinstall all requirements.

**Verify Python version:**
Ensure you're using Python 3.9 or higher.

---

#### Issue 7: Environment Variables Not Loading

**Symptoms:**
Application can't find OPENAI_API_KEY or other variables.

**Solutions:**

**Verify .env file exists:**
Check the file is in the project root directory.

**Check file format:**
Ensure no spaces around equals signs and no quotes unless needed.

**Manually load in Python:**
Test if python-dotenv is working correctly.

---

### Debug Mode

To get more detailed logs, you can run components in debug mode:

**FastAPI with debug logging:**
Modify main.py to enable debug mode and increase log level.

**Worker with verbose output:**
Add verbose flag when starting the worker.

---

## Stopping the Application

### Graceful Shutdown

To properly stop all components:

#### Step 1: Stop RQ Worker

Go to Terminal 2 and press Ctrl+C to send interrupt signal. Wait for the worker to finish processing current job.

#### Step 2: Stop FastAPI Server

Go to Terminal 1 and press Ctrl+C. Server will shut down gracefully.

#### Step 3: Stop Docker Services

Stop the Redis container while preserving data.

**To completely remove containers and volumes:**
Use down with volume flag to clean up everything.

---

## Development Workflow

### Recommended Development Process

#### Making Code Changes

**To modify worker logic:**
1. Stop the RQ worker (Ctrl+C in Terminal 2)
2. Edit worker.py file
3. Save changes
4. Restart worker process

**To modify API endpoints:**
1. Stop FastAPI server (Ctrl+C in Terminal 1)
2. Edit server.py file
3. Save changes
4. Restart server (or use auto-reload)

#### Auto-Reload During Development

For faster iteration, enable auto-reload mode:

**FastAPI auto-reload:**
Modify main.py to add reload parameter, or start server with reload flag using uvicorn directly.

**Worker auto-reload:**
Workers don't support auto-reload by default. Consider using a process manager or manually restart after changes.

---

## Production Deployment

### Deployment Checklist

When deploying to production, consider these important changes:

#### 1. Environment Configuration

- Use production-grade Redis (not Docker Compose)
- Enable Redis persistence and clustering
- Use secure connection strings
- Set proper CORS policies in FastAPI
- Enable HTTPS/TLS

#### 2. Process Management

**Use a process manager like systemd, supervisor, or PM2:**

- Ensure workers restart automatically on crash
- Run multiple workers for redundancy
- Monitor worker health
- Configure logging to files

#### 3. Scalability

**Horizontal Scaling:**
- Deploy multiple worker instances across servers
- Use load balancer for API servers
- Scale Redis using Redis Cluster or managed service

**Vertical Scaling:**
- Increase worker memory for larger contexts
- Use faster Redis instances
- Optimize Qdrant for production workload

#### 4. Monitoring

**Implement monitoring for:**
- API request latency and error rates
- Queue depth and processing time
- Worker health and job failure rates
- OpenAI API usage and costs
- Redis memory usage

**Tools to consider:**
- Prometheus + Grafana for metrics
- Sentry for error tracking
- ELK stack for log aggregation

#### 5. Security

- Never commit .env file to version control
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- Implement API authentication and rate limiting
- Restrict network access to Redis and Qdrant
- Enable HTTPS for all public endpoints

#### 6. Backup and Recovery

- Regular backups of Qdrant vector database
- Redis persistence configuration (AOF + RDB)
- Document recovery procedures
- Test disaster recovery plan

---

## Monitoring and Maintenance

### Health Checks

**API Health:**
Set up automated health checks hitting the root endpoint at regular intervals.

**Worker Health:**
Monitor worker process status and restart if crashed.

**Redis Health:**
Check Redis memory usage and connection count.

**Qdrant Health:**
Monitor collection size and query performance.

### Log Management

**Important logs to monitor:**

**FastAPI Access Logs:**
Track all incoming requests with timestamps.

**Worker Processing Logs:**
Monitor job execution times and errors.

**Error Logs:**
Capture all exceptions and stack traces.

**Rotation:**
Configure log rotation to prevent disk space issues.

### Performance Tuning

**Optimize query performance:**
- Adjust Qdrant similarity threshold
- Limit number of search results
- Cache frequent queries

**Reduce OpenAI costs:**
- Use GPT-3.5-turbo for simpler queries
- Implement prompt caching
- Reduce context size where possible

**Worker optimization:**
- Adjust worker count based on load
- Monitor memory usage per job
- Set timeout limits for long-running jobs

---

## Additional Resources

**Official Documentation:**
- FastAPI: fastapi.tiangolo.com
- RQ: python-rq.org
- Qdrant: qdrant.tech/documentation
- OpenAI: platform.openai.com/docs
- LangChain: python.langchain.com

**Community Support:**
- FastAPI Discussions: github.com/tiangolo/fastapi/discussions
- RQ GitHub Issues: github.com/rq/rq/issues
- Qdrant Discord: qdrant.to/discord

---

## Summary

You now have a complete guide to running the RAG Queue project. The key steps are:

1. Install prerequisites (Python, Docker, API keys)
2. Set up virtual environment and install dependencies
3. Configure environment variables in .env file
4. Start Redis via Docker Compose
5. Start FastAPI server in one terminal
6. Start RQ worker in another terminal
7. Test using the API endpoints

Remember: All three components (Redis, API Server, Worker) must be running simultaneously for the system to function properly.

For production deployments, follow the additional guidelines on security, monitoring, and scalability to ensure a robust and reliable system.
