# storage.py
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from constants import STORAGE_FILE, INACTIVITY_DAYS

os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

class Storage:
    def __init__(self, path: str = STORAGE_FILE):
        self.path = path
        if not os.path.exists(self.path):
            self._write({"users": {}, "leaderboard": {}})
        self.data = self._read()

    def _read(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Users: {user_id: {"name": str, "registered_games": [], "last_active": iso, "joined_at": iso}}
    def register_user(self, user_id: str, name: str):
        self.data = self._read()
        users = self.data.setdefault("users", {})
        users.setdefault(user_id, {
            "name": name,
            "registered_games": [],
            "last_active": _now_iso(),
            "joined_at": _now_iso()
        })
        self._write(self.data)

    def touch_user(self, user_id: str):
        self.data = self._read()
        if user_id in self.data.get("users", {}):
            self.data["users"][user_id]["last_active"] = _now_iso()
            self._write(self.data)

    def unregister_user_from_game(self, user_id: str, game_tag: str):
        self.data = self._read()
        if user_id in self.data.get("users", {}):
            regs = self.data["users"][user_id].get("registered_games", [])
            if game_tag in regs:
                regs.remove(game_tag)
                self._write(self.data)

    def register_user_for_game(self, user_id: str, game_tag: str):
        self.data = self._read()
        users = self.data.setdefault("users", {})
        users.setdefault(user_id, {"name": "Unknown", "registered_games": [], "last_active": _now_iso(), "joined_at": _now_iso()})
        regs = users[user_id].setdefault("registered_games", [])
        if game_tag not in regs:
            regs.append(game_tag)
        users[user_id]["last_active"] = _now_iso()
        self._write(self.data)

    def get_user(self, user_id: str):
        self.data = self._read()
        return self.data.get("users", {}).get(user_id)

    def active_users_for_game(self, game_tag: str):
        self.data = self._read()
        out = []
        for uid, u in self.data.get("users", {}).items():
            if game_tag in u.get("registered_games", []):
                out.append({"id": uid, "name": u.get("name"), "last_active": u.get("last_active")})
        return out

    def cleanup_inactive_leaderboard(self):
        """
        ارجع True إذا تم تغيير شيء. سيبقي أسماء ونقاط لكن يزيل من لائحة التسجيل بعد 30 يوم عدم نشاط.
        """
        changed = False
        self.data = self._read()
        cutoff = datetime.now(timezone.utc) - timedelta(days=INACTIVITY_DAYS)
        for uid, u in list(self.data.get("users", {}).items()):
            try:
                last = datetime.fromisoformat(u.get("last_active"))
            except Exception:
                continue
            if last < cutoff:
                # ازالة من التسجيلات (لن نحذف المستخدم أو نقاطه)
                if u.get("registered_games"):
                    u["registered_games"] = []
                    changed = True
        if changed:
            self._write(self.data)
        return changed
