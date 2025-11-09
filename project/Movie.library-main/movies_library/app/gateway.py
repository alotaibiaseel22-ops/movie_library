from __future__ import annotations
from typing import Dict, Any, List, Optional

from app.account_service import AccountService
from app.catalog_service import CatalogService
from app.recommendation_service import RecommendationService


class APIGateway:
    """
    Facade: single entry point for the CLI.
    """

    def __init__(self) -> None:
        self.accounts = AccountService()
        self.catalog = CatalogService()
        self.reco = RecommendationService()

    # Account
    def register_user(self, *args, **kwargs) -> Dict[str, Any]:
        return self.accounts.register_user(*args, **kwargs)

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        return self.accounts.authenticate(username, password)

    # Catalog
    def list_movies(self) -> List[Dict[str, Any]]:
        return self.catalog.list_movies()

    def add_movie(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        return self.catalog.add_movie(movie)

    # Recommendation
    def recommend(self, user_id: str, k: int = 5) -> List[Dict[str, Any]]:
        return self.reco.recommend_for_user(user_id, k=k)
