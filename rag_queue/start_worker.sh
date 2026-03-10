#!/bin/bash
# Start RQ worker with macOS fork safety disabled
# This prevents Objective-C runtime from killing forked processes

export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

cd "$(dirname "$0")"
source .venv/bin/activate
rq worker --with-scheduler
