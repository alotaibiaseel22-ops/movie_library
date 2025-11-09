from typing import List, Dict, Any


class MockAIAdapter:
    """Simple local AI adapter that ranks movies based on user preferences."""

    def recommend(self, user_profile: Dict[str, Any], movies: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
        prefs = set(p.lower() for p in user_profile.get("preferences", []))

        def score(m: Dict[str, Any]) -> int:
            genre = (m.get("genre") or "").lower()
            tags = [t.lower() for t in m.get("tags", [])]
            return int(genre in prefs) + sum(t in prefs for t in tags)

        ranked = sorted(movies, key=score, reverse=True)
        return ranked[:k]
