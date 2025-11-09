from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.db import JSONStore


class JSONAdapter:
    """
    Adapter over JSONStore (Singleton) providing CRUD for movies and users.
    Works purely with Python dicts (no models.py required).
    """

    def __init__(self) -> None:
        self.store = JSONStore()

    # ---------------- Movies ----------------
    def get_all_movies(self) -> List[Dict[str, Any]]:
        return list(self.store.movies)

    def get_movie(self, movie_id: str) -> Optional[Dict[str, Any]]:
        for m in self.store.movies:
            if m.get("id") == movie_id:
                return dict(m)
        return None

    def add_movie(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        if not movie.get("id") or not movie.get("title") or not movie.get("genre"):
            raise ValueError("movie must include 'id', 'title', and 'genre'")
        if self.get_movie(movie["id"]):
            raise ValueError(f"movie with id='{movie['id']}' already exists")

        self.store.movies.append(dict(movie))
        self.store.save_movies()
        return movie

    def update_movie(self, movie_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for i, m in enumerate(self.store.movies):
            if m.get("id") == movie_id:
                updated = dict(m)
                updated.update(patch)
                updated["id"] = movie_id  # ensure id stays the same
                self.store.movies[i] = updated
                self.store.save_movies()
                return updated
        return None

    def delete_movie(self, movie_id: str) -> bool:
        before = len(self.store.movies)
        self.store.movies = [m for m in self.store.movies if m.get("id") != movie_id]
        if len(self.store.movies) != before:
            self.store.save_movies()
            return True
        return False

    # ---------------- Users ----------------
    def get_all_users(self) -> List[Dict[str, Any]]:
        return list(self.store.users)

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        for u in self.store.users:
            if u.get("id") == user_id:
                return dict(u)
        return None

    def get_user_by_username(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("Use get_user_by_username(username) instead")  # guard against wrong call

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:  # type: ignore[override]
        uname = (username or "").strip().lower()
        for u in self.store.users:
            if (u.get("username") or "").strip().lower() == uname:
                return dict(u)
        return None

    def add_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        if not user.get("id") or not user.get("username"):
            raise ValueError("user must include 'id' and 'username'")
        if self.get_user(user["id"]):
            raise ValueError(f"user with id='{user['id']}' already exists")
        if self.get_user_by_username(user["username"]):
            raise ValueError(f"username '{user['username']}' is already taken")

        self.store.users.append(dict(user))
        self.store.save_users()
        return user

    def update_user(self, user_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for i, u in enumerate(self.store.users):
            if u.get("id") == user_id:
                updated = dict(u)
                updated.update(patch)
                updated["id"] = user_id  # keep ID unchanged
                self.store.users[i] = updated
                self.store.save_users()
                return updated
        return None

    def delete_user(self, user_id: str) -> bool:
        before = len(self.store.users)
        self.store.users = [u for u in self.store.users if u.get("id") != user_id]
        if len(self.store.users) != before:
            self.store.save_users()
            return True
        return False
