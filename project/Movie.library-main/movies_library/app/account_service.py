from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.adapters.json_adapter import JSONAdapter
from app.observer import EventBus


class AccountService:
    """
    Educational user management (plain-text passwords).
    """

    def __init__(self) -> None:
        self.storage = JSONAdapter()

    def list_users(self) -> List[Dict[str, Any]]:
        return self.storage.get_all_users()

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.storage.get_user(user_id)

    def register_user(
        self,
        user_id: str,
        name: str,
        username: str,
        password: str,
        preferences: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not user_id or not username or not password:
            raise ValueError("user_id, username, and password are required")

        user_doc: Dict[str, Any] = {
            "id": user_id,
            "name": name or username,
            "username": username.strip(),
            "password": password,
            "preferences": list(preferences or []),
        }
        created = self.storage.add_user(user_doc)
        EventBus.publish("USER_REGISTERED", {"user": created})
        return created

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.storage.get_user_by_username(username)
        if not user:
            return None
        return user if user.get("password") == password else None

    def update_user(self, user_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.storage.update_user(user_id, patch)

    def delete_user(self, user_id: str) -> bool:
        return self.storage.delete_user(user_id)
