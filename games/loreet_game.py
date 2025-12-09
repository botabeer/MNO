# games/loreet_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import THEMES
from database import Database

class LoreetGame:
    QUESTIONS = [
        "لو ريت تقدر ترجع الزمن لاي سنة تختار",
        "لو ريت عندك قوة خارقة وش بتكون",
        "لو ريت تقدر تتكلم مع حيوان اي حيوان تختار",
        "لو ريت تقدر تعيش في اي دولة وين تختار",
        "لو ريت عندك مليون ريال وش اول شي بتسويه",
        "لو ريت تقدر تقابل اي شخص من التاريخ من تختار",
        "لو ريت تقدر تغير شي في نفسك وش بيكون",
        "لو ريت تقدر تطير او تصير غير مرئي وش تختار",
        "لو ريت عندك سيارة احلامك وش موديلها",
        "لو ريت تقدر تعيش في اي عصر اي عصر تختار",
        "لو ريت تقدر تتعلم اي مهارة فورا وش تختار",
        "لو ريت تقدر تقرا عقول الناس او تسمع افكارهم وش تختار",
        "لو ريت تقدر تسافر لاي كوكب اي كوكب تزور",
        "لو ريت تقدر تعرف تاريخ وفاتك هل تبي تعرف",
        "لو ريت تقدر تغير قرار واحد في حياتك وش بيكون",
        "لو ريت تقدر تعيش تحت الماء او في الفضاء وش تختار",
        "لو ريت عندك قدرة تشفي اي مرض اي مرض تشفي",
        "لو ريت تقدر تتكلم كل لغات العالم هل تبي",
        "لو ريت تقدر توقف الزمن لساعة وحدة وش تسوي",
        "لو ريت عندك فرصة تعيش يوم واحد كشخص ثاني من تختار",
        "لو ريت تقدر تلغي شي من العالم وش بيكون",
        "لو ريت تقدر تضيف شي للعالم وش بيكون",
        "لو ريت عندك روبوت يسوي اي شي تبيه وش تخليه يسوي",
        "لو ريت تقدر تعرف اسرار شخص واحد من تختار",
        "لو ريت عندك فرصة تغير اسمك هل تغيره ولوش",
        "لو ريت تقدر تشوف المستقبل هل تبي تشوفه",
        "لو ريت عندك بيت احلامك وين موقعه",
        "لو ريت تقدر تاخذ اجازة سنة كاملة وش تسوي",
        "لو ريت عندك قدرة تتحكم بالطقس وش تسوي",
        "لو ريت تقدر تعيش بدون نوم هل تبي"
    ]

    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.total_questions = total_questions
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.registered = set()

    def register_player(self, uid, name):
        self.registered.add(uid)
        return True

    def start_game(self):
        self.questions = random.sample(self.QUESTIONS, min(self.total_questions, len(self.QUESTIONS)))
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()

    def _show_question(self, theme="light"):
        colors = THEMES.get(theme, THEMES["light"])
        question = self.questions[self.current_question]
        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "لو ريت",
                    "size": "xl",
                    "weight": "bold",
                    "color": colors["white"],
                    "align": "center"
                }],
                "backgroundColor": colors["primary"],
                "paddingAll": "16px",
                "cornerRadius": "12px"
            },
            {
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{self.current_question + 1}",
                        "size": "sm",
                        "color": colors["text_light"],
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": f"من {self.total_questions}",
                        "size": "sm",
                        "color": colors["text_light"],
                        "align": "end",
                        "flex": 1
                    }
                ],
                "margin": "md"
            },
            {"type": "separator", "margin": "md", "color": colors["border"]},
            {
                "type": "text",
                "text": question,
                "size": "md",
                "color": colors["text_dark"],
                "wrap": True,
                "align": "center",
                "margin": "lg",
                "weight": "bold"
            },
            {
                "type": "text",
                "text": "اجب على السؤال واكتب جاوب للانتقال",
                "size": "xs",
                "color": colors["text_light"],
                "align": "center",
                "margin": "md"
            },
            {"type": "separator", "margin": "md", "color": colors["border"]},
            {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "جاوب", "text": "جاوب"},
                        "style": "primary",
                        "color": colors["primary"],
                        "height": "sm"
                    }
                ]
            }
        ]
        return FlexMessage(
            alt_text="لو ريت",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": contents,
                    "backgroundColor": colors["card_bg"],
                    "paddingAll": "18px"
                }
            })
        )

    def next_question(self, theme="light"):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            return self._show_question(theme)
        return None

    def check_answer(self, text, uid, name, theme="light"):
        if uid not in self.registered:
            return None

        txt = text.strip().lower()
        
        if txt in ["جاوب", "التالي", "تخطي"]:
            if uid in self.answered_users:
                return None
            
            self.answered_users.add(uid)
            self.player_scores.setdefault(uid, {"name": name, "score": 0})
            self.player_scores[uid]["score"] += 1

            if self.current_question + 1 < self.total_questions:
                return {
                    "response": TextMessage(text=f"{name} شارك في السؤال\n+1 نقطة"),
                    "points": 1,
                    "correct": True,
                    "next_question": True
                }
            return self._end_game(theme)
        
        return None

    def _end_game(self, theme="light"):
        colors = THEMES.get(theme, THEMES["light"])
        if not self.player_scores:
            return {
                "response": TextMessage(text="انتهت اللعبة"),
                "game_over": True
            }

        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        winner = sorted_players[0][1]

        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "نتائج لو ريت",
                    "weight": "bold",
                    "size": "xl",
                    "color": colors["white"],
                    "align": "center"
                }],
                "backgroundColor": colors["primary"],
                "paddingAll": "12px",
                "cornerRadius": "8px"
            },
            {
                "type": "text",
                "text": f"الاكثر مشاركة: {winner['name']}",
                "size": "lg",
                "weight": "bold",
                "align": "center",
                "color": colors["success"],
                "margin": "lg"
            },
            {
                "type": "text",
                "text": f"المشاركات: {winner['score']}",
                "size": "md",
                "align": "center",
                "color": colors["text_dark"],
                "margin": "sm"
            },
            {"type": "separator", "margin": "md", "color": colors["border"]},
            {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "اعادة", "text": "لوريت"},
                        "style": "primary",
                        "color": colors["primary"],
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "البداية", "text": "بداية"},
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "margin": "md"
            }
        ]

        return {
            "response": FlexMessage(
                alt_text="نتائج لو ريت",
                contents=FlexContainer.from_dict({
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": contents,
                        "backgroundColor": colors["card_bg"],
                        "paddingAll": "16px"
                    }
                })
            ),
            "game_over": True,
            "won": True
        }
