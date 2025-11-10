from __future__ import annotations
from typing import Dict, Any, List, Optional
from pprint import pprint

from app.gateway import APIGateway
from app.account_service import AccountService


def print_header(current_user: Optional[Dict[str, Any]]):
    print("\n=== Movie Library ===")
    if current_user:
        print(f"Logged in as: {current_user.get('username')} ({current_user.get('name')})")
    else:
        print("Not logged in")
    print("-" * 30)
    print("1) Register")
    print("2) Login")
    print("3) List Movies")
    print("4) Get AI-Based Recommendations")
    print("q) Quit")


def register_user_cli(acc: AccountService):
    print("\nRegister a new user:")
    uid = input("User ID: ").strip()
    name = input("Name: ").strip()
    username = input("Username: ").strip()
    pwd = input("Password: ").strip()
    prefs_raw = input("Preferences (comma-separated): ").strip()
    prefs: List[str] = [p.strip() for p in prefs_raw.split(",")] if prefs_raw else []
    try:
        created = acc.register_user(uid, name, username, pwd, prefs)
        print("Registered successfully:")
        pprint(created)
    except Exception as e:
        print(f"Failed to register: {e}")


def login_cli(acc: AccountService) -> Optional[Dict[str, Any]]:
    print("\nLogin:")
    username = input("Username: ").strip()
    pwd = input("Password: ").strip()
    user = acc.authenticate(username, pwd)
    if user:
        print("Authenticated.")
        return user
    else:
        print("Invalid username or password.")
        return None


def list_movies(gw: APIGateway):
    movies = gw.list_movies()
    if not movies:
        print("No movies available yet.")
        return
    print(f"\nMovies ({len(movies)}):")
    for m in movies:
        print(f"- {m.get('id')}: {m.get('title')}  [{m.get('genre')}]  tags={m.get('tags', [])}")


def ensure_logged_in(current_user: Optional[Dict[str, Any]]) -> bool:
    if current_user is None:
        print("You must be logged in to use this feature. Please login first.")
        return False
    return True


def recommend_cli(gw: APIGateway, current_user: Dict[str, Any]):
    print("\nAI-Powered Recommendations:")
    try:
        k_txt = input("How many movie recommendations do you want? ").strip() or "5"
        k = int(k_txt)
    except ValueError:
        k = 5
    try:
        print("\nConnecting to AI...")
        print(f"Generating recommendations for {current_user['name']} ({current_user['id']})...")
        recs = gw.recommend(current_user["id"], k=k)
        if not recs:
            print("No recommendations returned.")
            return
        print(f"\nTop {len(recs)} recommendations for {current_user['name']}:")
        for i, r in enumerate(recs, 1):
            print(f"{i}. {r.get('title')} [{r.get('genre')}] tags={r.get('tags', [])}")
    except Exception as e:
        print(f"Failed to get recommendations: {e}")


def main():
    gw = APIGateway()
    acc = AccountService()
    current_user: Optional[Dict[str, Any]] = None

    # Show active AI backend (mock | openai | gemini)
    try:
        from app.adapters.api_adapter import APIAdapter
        backend = APIAdapter().backend_name
    except Exception:
        backend = "unknown"
    print(f"\n[AI Backend Active: {backend.upper()}]")

    while True:
        print_header(current_user)
        choice = input("> ").strip().lower()

        if choice == "1":
            register_user_cli(acc)
        elif choice == "2":
            current_user = login_cli(acc)
        elif choice == "3":
            list_movies(gw)
        elif choice == "4":
            if ensure_logged_in(current_user):
                recommend_cli(gw, current_user)
        elif choice in ("q", "quit", "exit"):
            print("\nGoodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
