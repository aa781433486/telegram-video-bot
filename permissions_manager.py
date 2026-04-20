import json
import os

PERMISSIONS_FILE = "permissions.json"
ADMIN_FILE = "admin_data.json"
USERS_FILE = "users_data.json"

AVAILABLE_TOOLS = {
    "veo3": "🎬 Veo 3 AI — توليد الفيديو بالذكاء الاصطناعي",
    "image_upscaler": "🖼️ تحسين جودة الصور",
    "prophet_stories": "📖 قصص الأنبياء الكرتونية",
}


def load_permissions():
    if not os.path.exists(PERMISSIONS_FILE):
        return {}
    with open(PERMISSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_permissions(data):
    with open(PERMISSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def grant_permission(username: str, tools: list):
    username = username.lstrip("@").lower()
    data = load_permissions()
    data[username] = tools
    save_permissions(data)


def revoke_permission(username: str):
    username = username.lstrip("@").lower()
    data = load_permissions()
    if username in data:
        del data[username]
        save_permissions(data)


def get_user_permissions(username: str) -> list:
    if not username:
        return []
    username = username.lstrip("@").lower()
    data = load_permissions()
    return data.get(username, [])


def get_all_permissions() -> dict:
    return load_permissions()


# ─── Admin Data ─────────────────────────────────────────────────────────────

def load_admin_data():
    if not os.path.exists(ADMIN_FILE):
        return {"admin_id": None}
    with open(ADMIN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_admin_data(data):
    with open(ADMIN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_admin_id():
    return load_admin_data().get("admin_id")


def set_admin_id(user_id: int):
    data = load_admin_data()
    data["admin_id"] = user_id
    save_admin_data(data)


def is_admin(user_id: int) -> bool:
    return get_admin_id() == user_id


# ─── Users Tracking ──────────────────────────────────────────────────────────

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_new_user(user_id: int) -> bool:
    users = load_users()
    return str(user_id) not in users


def register_user(user_id: int, username: str, first_name: str):
    users = load_users()
    users[str(user_id)] = {
        "username": username,
        "first_name": first_name,
    }
    save_users(users)


def get_all_users() -> dict:
    return load_users()
