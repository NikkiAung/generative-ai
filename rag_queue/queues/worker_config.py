"""
Worker configuration for macOS fork safety.

This must be imported BEFORE any other imports in the worker.
"""
import multiprocessing

# Use 'spawn' instead of 'fork' on macOS to avoid Objective-C fork safety issues
# This creates a new Python interpreter instead of forking the current one
multiprocessing.set_start_method('spawn', force=True)
