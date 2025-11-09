from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.adapters.json_adapter import JSONAdapter
from app.observer import EventBus
from app.factories import create_movie


class CatalogService:
    """
    Catalog operations (CRUD) on top of JSONAdapter.
    """

    REQUIRED_FIELDS = ("id", "title", "genre")

    def __init__(self) -> None:
        self.storage = JSONAdapter()

    def list_movies(self) -> List[Dict[str, Any]]:
        return self.storage.get_all_movies()

    def get_movie(self, movie_id: str) -> Optional[Dict[str, Any]]:
        return self.storage.get_movie(movie_id)

    def add_movie(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        # Normalize via factory (keeps id/title/genre/tags consistent)
        normalized = create_movie(
            title=movie.get("title", ""),
            genre=movie.get("genre", ""),
            tags=movie.get("tags", []),
            **movie
        )
        # Ensure required fields exist (adapter will also guard)
        for f in self.REQUIRED_FIELDS:
            if not normalized.get(f):
                raise ValueError(f"movie must include '{f}'")

        created = self.storage.add_movie(normalized)
        EventBus.publish("MOVIE_ADDED", {"movie": created})
        return created

    def update_movie(self, movie_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        patch = dict(patch or {})
        patch.pop("id", None)
        return self.storage.update_movie(movie_id, patch)

    def delete_movie(self, movie_id: str) -> bool:
        return self.storage.delete_movie(movie_id)
