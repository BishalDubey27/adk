"""
Embedding generation utilities for AlloyDB AI vector search.

Supports two modes:
  - Production: Vertex AI text-embedding model
  - Fallback: Gemini API-based embedding (when Vertex AI is unavailable)
"""
import hashlib
import struct
import structlog
from typing import List, Optional
from .config import settings

logger = structlog.get_logger()

# Cache for the Vertex AI client
_vertex_initialized = False


async def _init_vertex_ai():
    """Initialize Vertex AI SDK (one-time)."""
    global _vertex_initialized
    if _vertex_initialized:
        return
    
    try:
        import vertexai
        vertexai.init(
            project=settings.google_cloud_project,
            location=settings.google_cloud_region,
        )
        _vertex_initialized = True
        logger.info(
            "Vertex AI initialized",
            project=settings.google_cloud_project,
            region=settings.google_cloud_region,
        )
    except Exception as e:
        logger.warning(f"Failed to initialize Vertex AI: {e}")
        raise


async def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate a text embedding vector.
    
    Tries Vertex AI first, falls back to Gemini API, then to a deterministic
    hash-based embedding for local development.
    
    Args:
        text: The text to generate an embedding for
        
    Returns:
        List of floats (768 dimensions) or None on failure
    """
    # Try Vertex AI first
    embedding = await _generate_vertex_embedding(text)
    if embedding is not None:
        return embedding
    
    # Fallback to Gemini API
    embedding = await _generate_gemini_embedding(text)
    if embedding is not None:
        return embedding
    
    # Last resort: deterministic hash-based embedding (for local dev)
    logger.warning("Using hash-based fallback embedding (not suitable for production)")
    return _generate_hash_embedding(text)


async def generate_skill_embedding(skills: List[str]) -> Optional[List[float]]:
    """
    Generate an embedding from a list of skills.
    
    Concatenates skills into a descriptive string and generates an embedding.
    
    Args:
        skills: List of skill names (e.g., ["Python", "React", "FastAPI"])
        
    Returns:
        List of floats (768 dimensions) or None on failure
    """
    if not skills:
        return None
    
    # Create a rich text description from skills for better embedding quality
    skill_text = f"Professional skills and expertise in: {', '.join(skills)}. "
    skill_text += f"Experienced developer with knowledge of {' and '.join(skills)}."
    
    return await generate_embedding(skill_text)


async def generate_task_embedding(
    title: str, 
    description: str = "", 
    phase: str = ""
) -> Optional[List[float]]:
    """
    Generate an embedding for a task based on its title and description.
    
    Args:
        title: Task title
        description: Task description
        phase: Task phase (e.g., "development", "testing")
        
    Returns:
        List of floats (768 dimensions) or None on failure
    """
    text_parts = [f"Task: {title}"]
    if description:
        text_parts.append(f"Description: {description}")
    if phase:
        text_parts.append(f"Phase: {phase}")
    
    task_text = ". ".join(text_parts)
    return await generate_embedding(task_text)


async def _generate_vertex_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding using Vertex AI text-embedding model."""
    try:
        await _init_vertex_ai()
        
        from vertexai.language_models import TextEmbeddingModel
        
        model = TextEmbeddingModel.from_pretrained(settings.vertex_ai_embedding_model)
        embeddings = model.get_embeddings(
            [text],
            output_dimensionality=settings.vertex_ai_embedding_dimensions,
        )
        
        if embeddings and len(embeddings) > 0:
            logger.debug("Generated embedding via Vertex AI", text_length=len(text))
            return embeddings[0].values
        
        return None
    except Exception as e:
        logger.warning(f"Vertex AI embedding failed: {e}")
        return None


async def _generate_gemini_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding using Gemini API (fallback)."""
    if not settings.gemini_api_key:
        return None
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=settings.gemini_api_key)
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            output_dimensionality=settings.vertex_ai_embedding_dimensions,
        )
        
        if result and "embedding" in result:
            logger.debug("Generated embedding via Gemini API", text_length=len(text))
            return result["embedding"]
        
        return None
    except Exception as e:
        logger.warning(f"Gemini API embedding failed: {e}")
        return None


def _generate_hash_embedding(text: str) -> List[float]:
    """
    Generate a deterministic hash-based embedding (fallback for local dev).
    
    NOT suitable for production — embeddings won't be semantically meaningful.
    This ensures the application can start and test locally without GCP credentials.
    """
    dimensions = settings.vertex_ai_embedding_dimensions
    
    # Create a deterministic hash-based vector
    hash_bytes = hashlib.sha512(text.encode()).digest()
    
    # Extend hash to fill required dimensions
    extended = hash_bytes
    while len(extended) < dimensions * 4:  # 4 bytes per float
        extended += hashlib.sha512(extended).digest()
    
    # Convert to floats in [-1, 1] range
    embedding = []
    for i in range(dimensions):
        # Unpack 4 bytes as unsigned int, normalize to [-1, 1]
        val = struct.unpack('I', extended[i*4:(i+1)*4])[0]
        normalized = (val / (2**32 - 1)) * 2 - 1
        embedding.append(round(normalized, 6))
    
    # Normalize to unit length for cosine similarity
    magnitude = sum(x**2 for x in embedding) ** 0.5
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]
    
    return embedding
