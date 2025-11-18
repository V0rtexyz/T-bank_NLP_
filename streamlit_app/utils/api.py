"""
API client functions for T-Plexity backend
"""

import os
import httpx
from typing import Dict, List, Any, Optional

# Get API URL from environment variable or use default
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8002")
GENERATION_ENDPOINT = f"{API_BASE_URL}/generation/generate"
CLEAR_SESSION_ENDPOINT = f"{API_BASE_URL}/generation/clear_session"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

# HTTP client with timeout
client = httpx.Client(timeout=120.0)


def search_query(
    query: str,
    top_k: int = 5,
    use_rerank: bool = True,
    temperature: float = 0.7,
    llm_provider: str = "qwen",
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for investment information using AI
    
    Args:
        query: User question
        top_k: Number of documents to retrieve
        use_rerank: Whether to use reranking
        temperature: LLM temperature
        llm_provider: LLM provider to use
        session_id: Session ID for conversation history
    
    Returns:
        Dict with answer, sources, and timing information
    """
    try:
        payload = {
            "query": query,
            "top_k": top_k,
            "use_rerank": use_rerank,
            "temperature": temperature,
            "llm_provider": llm_provider
        }
        
        if session_id:
            payload["session_id"] = session_id
        
        response = client.post(
            GENERATION_ENDPOINT,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPError as e:
        raise Exception(f"API request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


def clear_session(session_id: str) -> Dict[str, Any]:
    """
    Clear conversation history for a session
    
    Args:
        session_id: Session ID to clear
    
    Returns:
        Dict with success status and message
    """
    try:
        response = client.post(
            CLEAR_SESSION_ENDPOINT,
            json={"session_id": session_id}
        )
        
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPError as e:
        raise Exception(f"API request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


def get_api_status() -> Dict[str, bool]:
    """
    Check if the API is healthy
    
    Returns:
        Dict with healthy status
    """
    try:
        response = client.get(HEALTH_ENDPOINT, timeout=5.0)
        return {"healthy": response.status_code == 200}
    except:
        return {"healthy": False}

