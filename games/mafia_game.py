# games/mafia_game.py
import random
import logging
from typing import Optional, Dict, Any, List

from linebot.v3.messaging import (
    TextMessage, FlexMessage, FlexContainer, PushMessageRequest
)

from constants import MAFIA_CONFIG, COLORS

logger = logging.getLogger(__name__)


class MafiaGame:
    """
    نسخة محسّنة من لعبة المافيا
    - أسرع في الاستجابة (أقصر Flex حيث لا داعي للتفاصيل الكثيرة)
    - أدوار افتراضية: mafia, detective, doctor, citizen
    - واجهات بسيطة ومتناسقة مع بقية الألعاب
    - واجهات خاصة (private) تُرسل عبر push_message
    - يرجع dict بالهيكلية: {"response": <Message|FlexMessage>|[...], ...}
    """

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

        # لاعبون: user_id -> { name, role, alive }
        self.players: Dict[str, Dict[str, Any]] = {}

        # مراحل: registration, night, day, voting, ended
        self.phase: str = "registration"
        self.day: int = 0

        # حالة مؤقتة
        self.votes: Dict[str, str] = {}          # voter_id -> target_id
        self.night_actions: Dict[str, str] = {}  # keys: mafia_target, doctor_target, detective_checks...
        self.group_id: Optional[str] = None

    # -----------------------
    # Helpers (lightweight)
    # -----------------------
    def _simple_flex(self, title: str, body_text: str, accent_color: Optional[str] = None):
        c = accent_color or COLORS["primary"]
        payload = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [{"type": "text", "text": title, "size": "md", "weight": "bold", "color": "#FFFFFF", "align": "center"}],
                        "backgroundColor": c,
                        "paddingAll": "10px",
                        "cornerRadius": "8px"
                    },
                    {"type": "text", "text": body_text, "size": "sm", "color": COLORS["text_dark"], "wrap": True, "margin": "md"}
                ],
                "backgroundColor": COLORS["card_bg"],
                "paddingAll": "12px"
            }
        }
        return FlexMessage(alt_text=title, contents=FlexContainer.from_dict(payload))

    def _text(self, txt: str):
        return TextMessage(text=txt)

    def _player_list_text(self) -> str:
        if not self.players:
            return "لا يوجد لاعبون مسجلون"
        lines = []
        for i, p in enumerate(self.players.values(), 1):
            status = "حيا" if p.get("alive", True) else "ميت"
            lines.append(f"{i}. {p['name']} — {status}")
        return "\n".join(lines)

    # -----------------------
    # Registration / UI
    # -----------------------
    def start_game(self):
        return {"response": self.registration_flex()}

    def registration_flex(self):
        player_count = len(self.players)
        min_players = MAFIA_CONFIG.get("min_players", 4)
        status_color = COLORS["success"] if player_count >= min_players else COLORS["warning"]
        status_text = f"{player_count} لاعب مسجل"
        if player_count < min_players:
            status_text += f"\nالحد الأدنى: {min_players} لاعبين"

        # Build compact flex
        body_text = status_text + "\n\n" + self._player_list_text()
        return self._simple_flex("لعبة المافيا", body_text, accent_color=status_color)

    def explanation_flex(self):
        body_text = (
            "خطوات سريعة:\n"
            "1) اضغط انضم مافيا للتسجيل\n"
            "2) عند اكتمال العدد ابدأ بـ 'بدء مافيا'\n"
            "الليل: المافيا تكتب 'اقتل اسم' في الخاص\n"
            "المحقق: 'افحص اسم' في الخاص\n"
            "الدكتور: 'احمي اسم' في الخاص\n"
            "النهار: في المجموعة ناقش ثم 'تصويت مافيا' ثم 'صوت اسم' ثم 'إنهاء التصويت'"
        )
        return self._simple_flex("شرح لعبة المافيا", body_text)

    # -----------------------
    # Player management
    # -----------------------
    def add_player(self, user_id: str, name: str):
        if self.phase != "registration":
            return {"response": self._text("اللعبة بدأت بالفعل")}
        if user_id in self.players:
            return {"response": self._text("أنت مسجل بالفعل")}
        # Add simple player structure
        self.players[user_id] = {"name": name, "role": None, "alive": True}
        return {"response": self.registration_flex()}

    def assign_roles(self):
        if self.phase != "registration":
            return {"response": self._text("اللعبة في طور التشغيل بالفعل")}
        min_players = MAFIA_CONFIG.get("min_players", 4)
        if len(self.players) < min_players:
            return {"response": self._text(f"عدد اللاعبين غير كافٍ. الحد الأدنى {min_players} لاعبين")}

        # Prepare roles
        base_roles = ["mafia", "detective", "doctor"]
        remaining = max(0, len(self.players) - len(base_roles))
        roles = base_roles + ["citizen"] * remaining
        random.shuffle(roles)

        # Assign deterministically to keys order to be stable/faster
        for (uid, player), role in zip(list(self.players.items()), roles):
            player["role"] = role
            try:
                self._send_role_private(uid, role)
            except Exception as e:
                logger.exception("خطأ أثناء إرسال الدور الخاص", exc_info=e)
                # continue anyway

        self.phase = "night"
        self.day = 1
        self.votes.clear()
        self.night_actions.clear()

        return {"response": [self._text("تم توزيع الأدوار — تحقق من رسائلك الخاصة"), self._night_flex()]}

    def _send_role_private(self, user_id: str, role: str):
        role_info = {
            "mafia": {"title": "أنت المافيا", "desc": "كل ليلة: اكتب في الخاص 'اقتل اسم' لاختيار ضحية", "color": "#8B0000"},
            "detective": {"title": "أنت المحقق", "desc": "كل ليلة: اكتب في الخاص 'افحص اسم' لمعرفة إذا كان مافيا أم لا", "color": "#1E90FF"},
            "doctor": {"title": "أنت الدكتور", "desc": "كل ليلة: اكتب في الخاص 'احمي اسم' لحماية لاعب (أو 'احمي نفسي')", "color": "#32CD32"},
            "citizen": {"title": "أنت مواطن", "desc": "دورك: التصويت بالنهار لمساعدة كشف المافيا", "color": "#808080"},
        }
        info = role_info.get(role, role_info["citizen"])

        # Small flex for private role
        payload = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {"type": "text", "text": "دورك السري", "size": "sm", "weight": "bold", "color": "#FFFFFF", "align": "center"},
                    {"type": "separator", "margin": "md", "color": COLORS["border"]},
                    {"type": "text", "text": info["title"], "size": "lg", "weight": "bold", "align": "center", "margin": "md"},
                    {"type": "text", "text": info["desc"], "size": "sm", "wrap": True, "margin": "md"}
                ],
                "backgroundColor": COLORS["card_bg"],
                "paddingAll": "12px"
            }
        }
        flex = FlexMessage(alt_text="دورك في المافيا", contents=FlexContainer.from_dict(payload))

        # push message to user (best-effort)
        try:
            self.line_bot_api.push_message(PushMessageRequest(to=user_id, messages=[flex]))
        except Exception:
            logger.exception("فشل إرسال رسالة الدور الخاص", exc_info=True)

    # -----------------------
    # Night / Day flow
    # -----------------------
    def _night_flex(self):
        alive_count = sum(1 for p in self.players.values() if p["alive"])
        body_text = f"اليوم {self.day} — الليل\nاللاعبون الأحياء: {alive_count}\nتحقق من رسائلك الخاصة لأداء دورك الليلي"
        return self._simple_flex("مرحلة الليل", body_text, accent_color="#2C3E50")

    def process_night(self):
        """
        تنفّذ إجراءات الليل: أولاً تحقق من هدف المافيا، ثم الدّكتور.
        قواعد مبسطة: إذا كان الهدف الذي اختارته المافيا محميًا من الدكتور ليلةً واحدة، لا يموت.
        """
        if self.phase != "night":
            return {"response": self._text("الآن ليس وقت الليل")}

        msgs: List[TextMessage] = []
        mafia_target = self.night_actions.get("mafia_target")
        doctor_target = self.night_actions.get("doctor_target")

        if mafia_target:
            # if mafia_target equals doctor_target -> doctor saved
            if mafia_target == doctor_target:
                msgs.append(self._text("طلع النهار...\nلم يُقتل أحد الليلة. الدكتور أنقذ الضحية."))
            else:
                # kill target if alive
                if self.players.get(mafia_target, {}).get("alive", False):
                    self.players[mafia_target]["alive"] = False
                    victim_name = self.players[mafia_target]["name"]
                    msgs.append(self._text(f"طلع النهار...\nتم قتل {victim_name}"))
                else:
                    msgs.append(self._text("طلع النهار...\nلم يُقتل أحد الليلة"))
        else:
            msgs.append(self._text("طلع النهار...\nلم تُنفّذ عملية قتل الليلة"))

        # reset night actions
        self.night_actions.clear()
        self.phase = "day"

        # check winner
        winner = self._check_winner()
        if winner:
            return winner

        # return day flex + messages
        return {"response": msgs + [self._day_flex()]}

    def _day_flex(self):
        alive_players = [(uid, p) for uid, p in self.players.items() if p["alive"]]
        names = [p["name"] for _, p in alive_players]
        body_text = f"اليوم {self.day} — النهار\nاللاعبون الأحياء:\n" + ("\n".join(names) if names else "لا أحد")
        return self._simple_flex("مرحلة النهار", body_text, accent_color="#F39C12")

    # -----------------------
    # Voting
    # -----------------------
    def start_voting(self):
        if self.phase not in ["day", "voting"]:
            return {"response": self._text("ليس وقت التصويت")}
        self.phase = "voting"
        self.votes.clear()
        return {"response": self._text("بدأ التصويت — اكتب: صوت اسم")}

    def vote(self, user_id: str, target_name: str):
        if self.phase != "voting":
            return {"response": self._text("ليس وقت التصويت")}
        if user_id not in self.players or not self.players[user_id]["alive"]:
            return {"response": self._text("لا يمكنك التصويت")}
        # find target id
        target_id = None
        for uid, p in self.players.items():
            if p["name"] == target_name and p["alive"]:
                target_id = uid
                break
        if not target_id:
            return {"response": self._text("لا يوجد لاعب بهذا الاسم أو هو غير حي")}
        self.votes[user_id] = target_id
        return {"response": self._text(f"تم التصويت لـ {target_name}")}

    def end_voting(self):
        if self.phase != "voting":
            return {"response": self._text("الآن ليس وقت إنهاء التصويت")}
        if not self.votes:
            # no votes -> go night
            self.phase = "night"
            self.day += 1
            return {"response": [self._text("لم يتم التصويت. الانتقال لليل"), self._night_flex()]}

        # tally
        tally: Dict[str, int] = {}
        for t in self.votes.values():
            tally[t] = tally.get(t, 0) + 1

        # find highest votes (if tie, pick random among top)
        max_votes = max(tally.values())
        candidates = [uid for uid, c in tally.items() if c == max_votes]
        executed = random.choice(candidates)
        executed_name = self.players[executed]["name"]
        executed_role = self.players[executed]["role"]

        # execute
        self.players[executed]["alive"] = False

        # reset voting
        self.votes.clear()
        self.phase = "night"
        self.day += 1

        # check winner
        winner = self._check_winner()
        if winner:
            return winner

        # return messages + night flex
        return {
            "response": [
                self._text(f"تم التصويت على {executed_name} وإعدامه — كان دوره: {self._translate_role(executed_role)}"),
                self._night_flex()
            ]
        }

    # -----------------------
    # Night commands (from private messages)
    # -----------------------
    def mafia_kill(self, user_id: str, target_name: str):
        if self.phase != "night":
            return {"response": self._text("ليس وقت الليل")}
        # verify mafia
        if user_id not in self.players or self.players[user_id].get("role") != "mafia":
            return {"response": self._text("أنت لست المافيا")}
        # cannot target dead or self
        for uid, p in self.players.items():
            if p["name"] == target_name and p["alive"] and uid != user_id:
                self.night_actions["mafia_target"] = uid
                return {"response": self._text(f"تم اختيار {target_name} كضحية الليلة")}
        return {"response": self._text("لا يوجد لاعب بهذا الاسم أو هو غير متاح")}

    def detective_check(self, user_id: str, target_name: str):
        if self.phase != "night":
            return {"response": self._text("ليس وقت الليل")}
        if user_id not in self.players or self.players[user_id].get("role") != "detective":
            return {"response": self._text("أنت لست المحقق")}
        # find target
        for uid, p in self.players.items():
            if p["name"] == target_name and p["alive"] and uid != user_id:
                role = p["role"]
                result = "مافيا" if role == "mafia" else "بريء"
                # record (light) and return
                self.night_actions.setdefault("detective_checks", []).append({"by": user_id, "target": uid, "result": result})
                return {"response": self._text(f"نتيجة الفحص: {target_name} — {result}")}
        return {"response": self._text("لا يوجد لاعب بهذا الاسم أو هو غير متاح")}

    def doctor_protect(self, user_id: str, target_name: str):
        if self.phase != "night":
            return {"response": self._text("ليس وقت الليل")}
        if user_id not in self.players or self.players[user_id].get("role") != "doctor":
            return {"response": self._text("أنت لست الدكتور")}
        # allow protecting self or others (one action per night)
        if target_name == "نفسي":
            self.night_actions["doctor_target"] = user_id
            return {"response": self._text("تم حمايتك الليلة")}
        for uid, p in self.players.items():
            if p["name"] == target_name and p["alive"]:
                self.night_actions["doctor_target"] = uid
                return {"response": self._text(f"تم حماية {target_name} الليلة")}
        return {"response": self._text("لا يوجد لاعب بهذا الاسم")}

    # -----------------------
    # Utilities & end
    # -----------------------
    def _translate_role(self, role: str) -> str:
        mapping = {"mafia": "المافيا", "detective": "المحقق", "doctor": "الدكتور", "citizen": "مواطن"}
        return mapping.get(role, role)

    def _check_winner(self):
        mafia_count = sum(1 for p in self.players.values() if p["alive"] and p.get("role") == "mafia")
        citizens_count = sum(1 for p in self.players.values() if p["alive"] and p.get("role") != "mafia")

        if mafia_count == 0:
            self.phase = "ended"
            return {"response": self._winner_flex("المواطنون"), "game_over": True}

        if mafia_count >= citizens_count:
            self.phase = "ended"
            return {"response": self._winner_flex("المافيا"), "game_over": True}

        return None

    def _winner_flex(self, winner_team: str):
        body_text = f"الفائز: {winner_team}"
        return self._simple_flex("انتهت اللعبة", body_text, accent_color=COLORS["primary"])

    # -----------------------
    # Main entry: process group/private commands
    # -----------------------
    def check_answer(self, text: str, user_id: str, display_name: str):
        """
        This is the main router for incoming messages related to mafia.
        It returns dict structures similar to previous implementation.
        """
        txt = (text or "").strip()

        # Group commands
        if txt == "انضم مافيا":
            return self.add_player(user_id, display_name)

        if txt == "بدء مافيا":
            return self.assign_roles()

        if txt == "شرح مافيا":
            return {"response": self.explanation_flex()}

        if txt == "حالة مافيا":
            alive = [p["name"] for p in self.players.values() if p["alive"]]
            dead = [p["name"] for p in self.players.values() if not p["alive"]]
            status = f"اليوم: {self.day}\nالمرحلة: {self.phase}\n\nالأحياء ({len(alive)}):\n"
            status += "\n".join(alive) if alive else "لا أحد"
            status += f"\n\nالموتى ({len(dead)}):\n"
            status += "\n".join(dead) if dead else "لا أحد"
            return {"response": self._text(status)}

        if txt == "إنهاء الليل":
            if self.phase == "night":
                return self.process_night()
            return {"response": self._text("ليس وقت الليل")}

        if txt == "تصويت مافيا":
            return self.start_voting()

        if txt.startswith("صوت "):
            target = txt.replace("صوت ", "", 1).strip()
            return self.vote(user_id, target)

        if txt == "إنهاء التصويت":
            return self.end_voting()

        # Private / role commands
        if txt.startswith("اقتل "):
            target = txt.replace("اقتل ", "", 1).strip()
            return self.mafia_kill(user_id, target)

        if txt.startswith("افحص "):
            target = txt.replace("افحص ", "", 1).strip()
            return self.detective_check(user_id, target)

        if txt.startswith("احمي "):
            target = txt.replace("احمي ", "", 1).strip()
            return self.doctor_protect(user_id, target)

        # Not handled
        return None
