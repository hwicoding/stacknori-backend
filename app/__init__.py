"""
Stacknori backend application package.

This module exposes helper functions so external entrypoints (e.g. Gunicorn)
can create the FastAPI application via `create_app()`.
"""

from .main import create_app

__all__ = ("create_app",)

