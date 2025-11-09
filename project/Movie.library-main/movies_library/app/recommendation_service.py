from __future__ import annotations
from typing import List, Dict, Any
from app.adapters.json_adapter import JSONAdapter
from app.adapters.api_adapter import APIAdapter
from app.observer import EventBus


class RecommendationService:
    """
    Connects JSONAdapter (data source) with APIAdapter (AI backend selector)
    to generate personalized movie recommendations.
    """

    def __init__(self) -> None:
        self.storage = JSONAdapter()
        self.ai = APIAdapter()  # reads env AI_BACKEND
        self._cache: Dict[tuple, List[Dict[str, Any]]] = {}

        # Simple observer usage: invalidate cache when data changes
        EventBus.subscribe("MOVIE_ADDED", lambda _: self._cache.clear())
        EventBus.subscribe("USER_REGISTERED", lambda p: self._cache.pop((p["user"]["id"], 5), None))

    def recommend_for_user(self, user_id: str, k: int = 5) -> List[Dict[str, Any]]:
        key = (user_id, int(k))
        if key in self._cache:
            return self._cache[key]

        user = self.storage.get_user(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        movies = self.storage.get_all_movies()
        if not movies:
            raise RuntimeError("No movies available in the catalog.")

        recs = self.ai.recommend(user_profile=user, movies=movies, k=k) or []
        recs = recs[:k]
        self._cache[key] = recs
        return recs
