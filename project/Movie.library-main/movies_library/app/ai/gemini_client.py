from typing import List, Dict, Any
import os
import google.generativeai as genai


class GeminiAdapter:
    """Adapter that integrates Google Gemini for movie recommendations with dynamic model selection."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing Gemini API key. Please set GEMINI_API_KEY.")
        genai.configure(api_key=api_key)

        # 1) If user explicitly sets a model, try to use it
        preferred = os.getenv("GEMINI_MODEL")
        # 2) Otherwise, try these in order (varies by account/region/version)
        fallbacks = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-pro",
            "text-bison-001",  # legacy but often available
        ]
        self.model_name = self._select_model(preferred, fallbacks)
        self.model = genai.GenerativeModel(self.model_name)

    def _select_model(self, preferred: str | None, fallbacks: List[str]) -> str:
        """Pick a model that supports generateContent. Prefer explicit setting, else fallbacks, else first available."""
        try:
            models = list(genai.list_models())
        except Exception as e:
            raise RuntimeError(f"Failed to list Gemini models. Check your API key/permissions. Details: {e}")

        def supports_generate(m) -> bool:
            # Some SDKs expose 'supported_generation_methods' containing 'generateContent'
            methods = getattr(m, "supported_generation_methods", None) or []
            methods = [str(x) for x in methods]
            return ("generateContent" in methods) or ("generate_content" in methods)

        available = {getattr(m, "name", "").split("/")[-1]: m for m in models if supports_generate(m)}

        # If user requested a specific model, honor it if available
        if preferred and preferred in available:
            return preferred

        # Try fallbacks in order
        for cand in fallbacks:
            if cand in available:
                return cand

        # As a last resort, pick the first supporting model if any
        if available:
            return next(iter(available.keys()))

        raise RuntimeError(
            "No Gemini model that supports generateContent is available for your account/API version. "
            "Enable Generative Language API for your key, or set GEMINI_MODEL to a model visible in your account."
        )

    def recommend(self, user_profile: Dict[str, Any], movies: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
        prefs = ", ".join(user_profile.get("preferences", []))
        catalog = "\n".join([f"- {m.get('title','')} [{m.get('genre','')}] tags={', '.join(m.get('tags', []))}" for m in movies])

        prompt = (
            "You are a movie recommendation assistant.\n"
            f"User preferences: {prefs}\n"
            "Catalog:\n"
            f"{catalog}\n\n"
            f"Task: Recommend the top {k} movies from the catalog that best match the user preferences. "
            "Respond with a plain list of titles only, one per line, no numbering and no extra text."
        )

        try:
            resp = self.model.generate_content(prompt)
            text = (resp.text or "").strip()
        except Exception as e:
            # Graceful fallback: basic preference ranking
            prefs_set = set(p.lower() for p in user_profile.get("preferences", []))
            def score(m: Dict[str, Any]) -> int:
                g = (m.get("genre") or "").lower()
                tags = [t.lower() for t in m.get("tags", [])]
                return int(g in prefs_set) + sum(t in prefs_set for t in tags)
            return sorted(movies, key=score, reverse=True)[:k]

        # Map generated titles back to our catalog
        lines = [ln.strip("- •\t ").strip() for ln in text.splitlines() if ln.strip()]
        ranked: List[Dict[str, Any]] = []
        lower_by_title = {m["title"].lower(): m for m in movies}

        for ln in lines:
            key = ln.lower()
            if key in lower_by_title:
                ranked.append(lower_by_title[key])
            else:
                # Try loose match by genre/tags if a title wasn't matched
                for m in movies:
                    blob = (m.get("title","") + " " + m.get("genre","") + " " + " ".join(m.get("tags", []))).lower()
                    if key in blob:
                        ranked.append(m)
                        break
            if len(ranked) >= k:
                break

        if not ranked:
            # Fallback: quick preference sort
            prefs_set = set(p.lower() for p in user_profile.get("preferences", []))
            def score(m: Dict[str, Any]) -> int:
                g = (m.get("genre") or "").lower()
                tags = [t.lower() for t in m.get("tags", [])]
                return int(g in prefs_set) + sum(t in prefs_set for t in tags)
            ranked = sorted(movies, key=score, reverse=True)

        return ranked[:k]
