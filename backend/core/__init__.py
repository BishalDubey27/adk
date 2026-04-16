"""Core module for Tech Sarathi backend."""
from .config import settings

__all__ = ["settings"]

# Lazy import for embeddings (avoid import errors if dependencies missing)
def get_embeddings():
    from . import embeddings
    return embeddings
