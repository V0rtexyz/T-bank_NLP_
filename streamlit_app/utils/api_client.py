"""API client for T-Plexity backend services"""

import httpx
import logging
from typing import Dict, List, Optional, Any
import streamlit as st

logger = logging.getLogger(__name__)


class TPlexityAPI:
    """Client for T-Plexity backend APIs"""
    
    def __init__(
        self,
        retriever_url: str = "http://localhost:8001",
        generation_url: str = "http://localhost:8002",
        timeout: float = 30.0
    ):
        self.retriever_url = retriever_url.rstrip("/")
        self.generation_url = generation_url.rstrip("/")
        self.timeout = timeout
    
    async def search_documents(
        self,
        query: str,
        top_k: int = 10,
        top_n: int = 10,
        use_rerank: bool = False,
        sparse_weight: float = 0.5,
        dense_weight: float = 0.5,
    ) -> Dict[str, Any]:
        """Search for documents using the Retriever API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.retriever_url}/retriever/search",
                    json={
                        "query": query,
                        "top_k": top_k,
                        "top_n": top_n,
                        "use_rerank": use_rerank,
                        "sparse_weight": sparse_weight,
                        "dense_weight": dense_weight,
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error searching documents: {e}")
            return {"results": [], "total": 0, "error": str(e)}
    
    async def generate_answer(
        self,
        query: str,
        top_k: int = 5,
        use_rerank: bool = True,
        temperature: float = 0.3,
        max_tokens: int = 1000,
        llm_provider: str = "openai",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate an answer using the Generation API (RAG)"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "query": query,
                    "top_k": top_k,
                    "use_rerank": use_rerank,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "llm_provider": llm_provider,
                }
                if session_id:
                    payload["session_id"] = session_id
                
                response = await client.post(
                    f"{self.generation_url}/generation/generate",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": f"Error: {str(e)}",
                "detailed_answer": f"Error: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    async def clear_session(self, session_id: str) -> Dict[str, Any]:
        """Clear conversation history for a session"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.generation_url}/generation/clear-session",
                    json={"session_id": session_id}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error clearing session: {e}")
            return {"success": False, "message": str(e)}
    
    async def health_check(self, service: str = "retriever") -> bool:
        """Check if a service is healthy"""
        try:
            url = self.retriever_url if service == "retriever" else self.generation_url
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                return response.status_code == 200
        except:
            return False


def get_api_client() -> TPlexityAPI:
    """Get or create API client (singleton pattern)"""
    if "api_client" not in st.session_state:
        retriever_url = st.secrets.get("RETRIEVER_URL", "http://localhost:8001")
        generation_url = st.secrets.get("GENERATION_URL", "http://localhost:8002")
        
        st.session_state.api_client = TPlexityAPI(
            retriever_url=retriever_url,
            generation_url=generation_url
        )
    
    return st.session_state.api_client

