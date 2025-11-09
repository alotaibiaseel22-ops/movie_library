from __future__ import annotations
from typing import Any, Dict, List
from infra.database_manager import DatabaseManager

class JSONStore:
    def __init__(self): self._mgr = DatabaseManager()
    @property
    def movies(self) -> List[Dict[str, Any]]: return self._mgr.movies
    @movies.setter
    def movies(self, v: List[Dict[str, Any]]): self._mgr.movies = v
    @property
    def users(self) -> List[Dict[str, Any]]: return self._mgr.users
    @users.setter
    def users(self, v: List[Dict[str, Any]]): self._mgr.users = v
    def save_movies(self): self._mgr.save_movies()
    def save_users(self): self._mgr.save_users()
    def save_all(self): self._mgr.save_all()
    def reload(self): self._mgr.reload()
