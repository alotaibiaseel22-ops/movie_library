from typing import Dict, Any, List
from uuid import uuid4

def create_movie(title: str, genre: str, tags: List[str] | None = None, **extra) -> Dict[str, Any]:
    return {
        "id": extra.get("id", f"m-{uuid4().hex[:8]}"),
        "title": title.strip(),
        "genre": genre.strip(),
        "tags": list(tags or []),
        **{k: v for k, v in extra.items() if k != "id"}
    }

def create_user(name: str, username: str, password: str, preferences: List[str] | None = None, **extra) -> Dict[str, Any]:
    return {
        "id": extra.get("id", f"u-{uuid4().hex[:8]}"),
        "name": name.strip(),
        "username": username.strip(),
        "password": password,
        "preferences": list(preferences or []),
        **{k: v for k, v in extra.items() if k != "id"}
    }

def create_reco_request(user_id: str, k: int = 5) -> Dict[str, Any]:
    return {"user_id": user_id, "top_k": int(k)}
