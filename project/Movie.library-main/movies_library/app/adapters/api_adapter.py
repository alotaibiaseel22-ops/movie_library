from __future__ import annotations
from typing import Any, Dict, List, Protocol, runtime_checkable
import os


@runtime_checkable
class Recommender(Protocol):
    def recommend(self, user_profile: Dict[str, Any], movies: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
        ...


class APIAdapter:
    """
    Unified AI adapter. Chooses the backend via:
      - constructor arg `backend`, or
      - env var AI_BACKEND in {"mock", "openai", "gemini"} (default: "mock").
    """

    def __init__(self, backend: str | None = None) -> None:
        name = (backend or os.getenv("AI_BACKEND", "mock")).strip().lower()

        if name == "openai":
            from app.ai.openai_client import OpenAIAdapter
            self.client: Recommender = OpenAIAdapter()
        elif name == "gemini":
            from app.ai.gemini_client import GeminiAdapter
            self.client = GeminiAdapter()
        else:
            from app.ai.mock_client import MockAIAdapter
            name = "mock"
            self.client = MockAIAdapter()

        self.backend_name = name

    def recommend(self, user_profile: Dict[str, Any], movies: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
        return self.client.recommend(user_profile=user_profile, movies=movies, k=k)
