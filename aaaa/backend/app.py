"""Compatibility entrypoint for platforms that auto-detect app.py.

This module re-exports the FastAPI application from server.py so deployments do
not boot a stale Flask app instead of the current backend.
"""

from server import app

application = app