from typing import List, Dict, Any
import os
from openai import OpenAI


class OpenAIAdapter:
    """Adapter that integrates OpenAI models for movie recommendations."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenAI API key. Please set OPENAI_API_KEY.")
        self.client = OpenAI(api_key=api_key)

    def recommend(self, user_profile: Dict[str, Any], movies: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
        prefs = ", ".join(user_profile.get("preferences", []))
        movie_titles = ", ".join([m["title"] for m in movies])

        prompt = (
            f"The user prefers: {prefs}.\n"
            f"Movies available: {movie_titles}.\n"
            f"Suggest the top {k} movies most aligned with their preferences."
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a movie recommendation assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        text = response.choices[0].message.content.strip()
        ranked = [m for m in movies if any(t.lower() in text.lower() for t in [m["title"], m["genre"]])]
        return ranked[:k] if ranked else movies[:k]
