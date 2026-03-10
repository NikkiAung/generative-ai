#!/bin/bash
# Start RQ worker with proxy detection disabled
# Prevents urllib from calling macOS system proxy APIs

export NO_PROXY="*"
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

cd "$(dirname "$0")"
source .venv/bin/activate
rq worker --with-scheduler
