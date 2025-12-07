from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import (
    create_game_header,
    create_separator,
    create_action_buttons,
    create_winner_card
)

class MafiaGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

        # players: { user_id: {"name": "", "role": "", "alive": True } }
        self.players = {}

        #_votes: { target_id: [voters] }
        self.votes = {}

        self.roles = ["مافيا", "شرطي", "طبيب", "مواطن"]
        self.game_started = False
        self.day_phase = True   # True = نهار | False = ليل

        self.last_killed = None
        self.saved_player = None

    # ---------------------------------------------------------------
    # Start Game
    # ---------------------------------------------------------------
    def start_game(self, players):
        """
        players: list of (user_id, display_name)
        """

        # reset state
        self.players.clear()
        self.votes.clear()
        self.game_started = True
        self.day_phase = True
        self.last_killed = None
        self.saved_player = None

        # assign roles
        shuffled = random.sample(players, len(players))
        roles_pool = self._assign_roles(len(players))

        for i, (uid, name) in enumerate(shuffled):
            self.players[uid] = {
                "name": name,
                "role": roles_pool[i],
                "alive": True
            }

        return TextMessage(text="🎭 *بدأت لعبة المافيا!*\nتم توزيع الأدوار سرّياً.")

    # ---------------------------------------------------------------
    def _assign_roles(self, count):
        """توزيع أدوار ديناميكي حسب عدد اللاعبين"""

        result = []

        if count >= 4:
            result += ["مافيا"]

        if count >= 6:
            result += ["مافيا", "شرطي"]

        if count >= 7:
            result += ["طبيب"]

        # الباقي مواطنين
        while len(result) < count:
            result.append("مواطن")

        random.shuffle(result)
        return result

    # ---------------------------------------------------------------
    # Handle actions
    # ---------------------------------------------------------------

    def check_action(self, text, user_id):
        if not self.game_started:
            return None

        text = text.strip()

        if not self.players.get(user_id, {}).get("alive"):
            return TextMessage(text="❌ انت ميت وما تقدر تتصرف.")

        # نهار → تصويت
        if self.day_phase:
            if text.startswith("صوت "):
                target_name = text.replace("صوت", "").strip()
                return self._handle_vote(user_id, target_name)

            return TextMessage(text="في النهار يمكنك التصويت فقط بصيغة:\nصوت (اسم اللاعب)")

        # ليل → حسب الدور
        else:
            role = self.players[user_id]["role"]

            if role == "مافيا" and text.startswith("اقتل "):
                target_name = text.replace("اقتل", "").strip()
                return self._mafia_kill(user_id, target_name)

            if role == "شرطي" and text.startswith("افحص "):
                target_name = text.replace("افحص", "").strip()
                return self._detective_check(user_id, target_name)

            if role == "طبيب" and text.startswith("احمي "):
                target_name = text.replace("احمي", "").strip()
                return self._doctor_save(user_id, target_name)

            return TextMessage(text="هذا وقت الليل—تصرف حسب دورك.")

    # ---------------------------------------------------------------
    # Voting
    # ---------------------------------------------------------------

    def _handle_vote(self, voter_id, target_name):
        target_id = self._find_player_by_name(target_name)

        if not target_id:
            return TextMessage(text="❌ لم أجد هذا اللاعب.")

        if not self.players[target_id]["alive"]:
            return TextMessage(text="❌ هذا اللاعب ميت.")

        self.votes.setdefault(target_id, [])

        # منع التصويت مرتين
        for voters in self.votes.values():
            if voter_id in voters:
                return TextMessage(text="❌ لقد صوتت سابقاً.")

        self.votes[target_id].append(voter_id)

        return TextMessage(text=f"✔ تم تسجيل صوتك ضد: {self.players[target_id]['name']}")

    # ---------------------------------------------------------------
    # Night actions
    # ---------------------------------------------------------------

    def _mafia_kill(self, user_id, target_name):
        target_id = self._find_player_by_name(target_name)

        if not target_id:
            return TextMessage(text="❌ اللاعب غير موجود.")

        if not self.players[target_id]["alive"]:
            return TextMessage(text="❌ اللاعب ميت.")

        self.last_killed = target_id
        return TextMessage(text="🔪 تم اختيار الضحية. انتظر نهاية الليل.")

    def _detective_check(self, user_id, target_name):
        target_id = self._find_player_by_name(target_name)
        if not target_id:
            return TextMessage(text="❌ اللاعب غير موجود.")

        role = self.players[target_id]["role"]
        mafia = (role == "مافيا")

        return TextMessage(text=f"نتيجة الفحص: {'مافيا 😈' if mafia else 'ليس مافيا 😇'}")

    def _doctor_save(self, user_id, target_name):
        target_id = self._find_player_by_name(target_name)
        if not target_id:
            return TextMessage(text="❌ اللاعب غير موجود.")

        self.saved_player = target_id
        return TextMessage(text="🛡 تم تحديد الحماية.")

    # ---------------------------------------------------------------
    # End of day / night
    # ---------------------------------------------------------------

    def end_day(self):
        """تنفيذ نتيجة التصويت"""

        if not self.votes:
            return TextMessage(text="لم يصوت أحد. لا أحد خرج. 🔄")

        # حساب أعلى تصويت
        target = max(self.votes.items(), key=lambda x: len(x[1]))[0]

        self.players[target]["alive"] = False
        name = self.players[target]["name"]
        role = self.players[target]["role"]

        self.votes.clear()

        return TextMessage(text=f"🪦 تم إعدام: {name}\nكان دوره: {role}")

    def end_night(self):
        """تنفيذ القتل + الحماية"""

        if self.last_killed and self.last_killed != self.saved_player:
            self.players[self.last_killed]["alive"] = False
            killed_name = self.players[self.last_killed]["name"]
            msg = f"💀 قُتل اللاعب: {killed_name}"
        else:
            msg = "😇 لم يمت أحد الليلة!"

        self.last_killed = None
        self.saved_player = None

        return TextMessage(text=msg)

    # ---------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------

    def _find_player_by_name(self, name):
        for uid, p in self.players.items():
            if p["name"] == name:
                return uid
        return None
