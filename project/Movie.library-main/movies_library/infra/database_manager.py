from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json, threading, tempfile, os

class DatabaseManager:
    _instance: "DatabaseManager|None" = None
    _lock = threading.Lock()

    def __new__(cls, movies_path: str | Path = Path("data/movies.json"),
                     users_path: str | Path = Path("data/users.json")):
        with cls._lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst.movies_path = Path(movies_path)
                inst.users_path = Path(users_path)
                inst._load()
                cls._instance = inst
            return cls._instance

    def _load(self) -> None:
        self.movies: List[Dict[str, Any]] = self._read(self.movies_path)
        self.users:  List[Dict[str, Any]] = self._read(self.users_path)

    @staticmethod
    def _read(path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("[]", encoding="utf-8")
        txt = path.read_text(encoding="utf-8").strip() or "[]"
        try:
            data = json.loads(txt)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    @staticmethod
    def _atomic_write(path: Path, data: List[Dict[str, Any]]) -> None:
        fd, tmp = tempfile.mkstemp(prefix=path.name, dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush(); os.fsync(f.fileno())
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                try: os.remove(tmp)
                except OSError: pass

    def reload(self): self._load()
    def save_movies(self): self._atomic_write(self.movies_path, self.movies)
    def save_users(self):  self._atomic_write(self.users_path, self.users)
    def save_all(self):
        self._atomic_write(self.movies_path, self.movies)
        self._atomic_write(self.users_path, self.users)
