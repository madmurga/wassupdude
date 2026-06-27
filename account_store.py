import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


ACCOUNT_FILE = Path(__file__).resolve().parent / "math_accounts.json"
POINTS_BY_DIFFICULTY = {
    "easy": 5,
    "medium": 10,
    "hard": 15,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_username(username: str) -> str:
    return username.strip().lower()


def _empty_data() -> dict:
    return {"users": {}}


def load_account_data() -> dict:
    if not ACCOUNT_FILE.exists():
        return _empty_data()

    try:
        with ACCOUNT_FILE.open("r", encoding="utf-8") as account_file:
            data = json.load(account_file)
    except (OSError, json.JSONDecodeError):
        return _empty_data()

    if not isinstance(data, dict):
        return _empty_data()

    users = data.get("users", {})
    if not isinstance(users, dict):
        users = {}

    data["users"] = users
    return data


def save_account_data(data: dict) -> None:
    ACCOUNT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_path = ACCOUNT_FILE.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as account_file:
        json.dump(data, account_file, indent=2)
    os.replace(temp_path, ACCOUNT_FILE)


def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return salt, password_hash


def _valid_username(username: str) -> bool:
    return all(ch.isalnum() or ch in "_-" for ch in username)


def create_account(username: str, password: str) -> tuple[bool, str, Optional[str]]:
    display_name = username.strip()
    user_key = normalize_username(display_name)

    if not display_name:
        return False, "Enter a username.", None
    if len(user_key) < 3:
        return False, "Usernames must be at least 3 characters.", None
    if not _valid_username(display_name):
        return False, "Use only letters, numbers, underscores, or hyphens.", None
    if len(password) < 4:
        return False, "Passwords must be at least 4 characters.", None

    data = load_account_data()
    if user_key in data["users"]:
        return False, "That username already exists.", None

    salt, password_hash = _hash_password(password)
    data["users"][user_key] = {
        "username": display_name,
        "salt": salt,
        "password_hash": password_hash,
        "points": 0,
        "solved": 0,
        "created_at": _now_iso(),
        "last_seen": _now_iso(),
    }
    save_account_data(data)
    return True, "Account created.", user_key


def verify_password(password: str, account: dict) -> bool:
    salt = account.get("salt", "")
    saved_hash = account.get("password_hash", "")
    _, entered_hash = _hash_password(password, salt)
    return hmac.compare_digest(entered_hash, saved_hash)


def authenticate(username: str, password: str) -> tuple[bool, str, Optional[str]]:
    user_key = normalize_username(username)
    data = load_account_data()
    account = data["users"].get(user_key)

    if account is None or not verify_password(password, account):
        return False, "Incorrect username or password.", None

    account["last_seen"] = _now_iso()
    save_account_data(data)
    return True, "Signed in.", user_key


def get_account(user_key: Optional[str]) -> Optional[dict]:
    if not user_key:
        return None
    data = load_account_data()
    return data["users"].get(user_key)


def add_points_to_account(user_key: Optional[str], points: int) -> Optional[dict]:
    if not user_key or points <= 0:
        return None

    data = load_account_data()
    account = data["users"].get(user_key)
    if account is None:
        return None

    account["points"] = int(account.get("points", 0)) + points
    account["solved"] = int(account.get("solved", 0)) + 1
    account["last_seen"] = _now_iso()
    save_account_data(data)
    return account


def get_leaderboard_entries(limit: Optional[int] = None) -> list[dict]:
    data = load_account_data()
    entries = []

    for user_key, account in data["users"].items():
        entries.append(
            {
                "User": account.get("username", user_key),
                "Points": int(account.get("points", 0)),
                "Solved": int(account.get("solved", 0)),
            }
        )

    entries.sort(key=lambda row: (-row["Points"], -row["Solved"], row["User"].lower()))

    ranked_entries = []
    for index, entry in enumerate(entries, start=1):
        ranked_entries.append({"Rank": index, **entry})

    if limit is not None:
        return ranked_entries[:limit]
    return ranked_entries
