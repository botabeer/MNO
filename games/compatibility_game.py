from __future__ import annotations
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
from typing import Tuple, Optional
import hashlib
import re

from constants import COLORS


class CompatibilityGame:
    """
    لعبة نسبة التوافق – نسخة محسّنة:
    - قراءة الأسماء مهما كان التنسيق (مسافات، بدون مسافات، وجود رموز).
    - عدم قبول الأسماء الفارغة أو المليئة برموز فقط.
    - نفس النتيجة دائماً لنفس الأسماء باستخدام hashing ثابت.
    - واجهة FlexMessage محسنة ومتناسقة مع باقي الألعاب.
    """

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.waiting_for_names: bool = True
        self.SALT = "COMPATIBILITY_SALT_2024"  # لثبات النتائج وتحسين توزيعها

    # ---------------------------------------------------------------------
    # UI – Start
    # ---------------------------------------------------------------------
    def start_game(self) -> FlexMessage:
        self.waiting_for_names = True

        return FlexMessage(
            alt_text="نسبة التوافق",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        self._header("نسبة التوافق"),
                        self._instruction_block(),
                        self._examples_block()
                    ],
                    "backgroundColor": COLORS["card_bg"],
                    "paddingAll": "20px"
                }
            })
        )

    # ---------------------------------------------------------------------
    # Parsing Names – أقوى نسخـة
    # ---------------------------------------------------------------------
    def parse_names(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """تحليل الاسمَين من النص. يبحث عن 'و' بجميع أشكالها."""
        if not text:
            return None, None

        text = text.strip()

        # توحيد حرف "و"  
        text = re.sub(r"\s*و\s*", " و ", text)
        parts = [p.strip() for p in text.split(" و ") if p.strip()]

        if len(parts) < 2:
            return None, None

        name1, name2 = parts[0], " ".join(parts[1:])

        # حذف الرموز + ترك الأحرف العربية فقط
        name1 = self._clean_name(name1)
        name2 = self._clean_name(name2)

        if not name1 or not name2:
            return None, None

        return name1, name2

    def _clean_name(self, name: str) -> Optional[str]:
        """ينظّف الاسم من الرموز – ويبقي فقط حروف عربية ومسافات."""
        name = re.sub(r"[^أ-يa-zA-Z\s]", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name if len(name) >= 2 else None

    # ---------------------------------------------------------------------
    # Compatibility Calculation
    # ---------------------------------------------------------------------
    def calculate_compatibility(self, name1: str, name2: str) -> int:
        names_sorted = sorted([name1.lower(), name2.lower()])
        combined = (names_sorted[0] + "|" + names_sorted[1] + "|" + self.SALT)

        hash_value = int(hashlib.sha256(combined.encode()).hexdigest(), 16)
        return (hash_value % 51) + 50  # نسبة من 50% إلى 100%

    def get_compatibility_message(self, score: int) -> str:
        if score >= 90: return "توافق مثالي"
        if score >= 75: return "توافق ممتاز"
        if score >= 60: return "توافق جيد"
        return "توافق متوسط"

    def get_color(self, score: int) -> str:
        if score >= 90: return "#FF1493"
        if score >= 75: return "#FF69B4"
        if score >= 60: return "#FFB6C1"
        return COLORS["text_light"]

    # ---------------------------------------------------------------------
    # Main Logic
    # ---------------------------------------------------------------------
    def check_answer(self, answer, user_id, display_name):
        if not self.waiting_for_names:
            return None

        name1, name2 = self.parse_names(answer)

        if not name1 or not name2:
            return {
                "response": TextMessage(
                    text="❗ يرجى كتابة اسمين بالشكل التالي:\n\nالاسم و الاسم\n\nمثال:\nالحوت و عبير\nالقوس و الدلو"
                ),
                "points": 0, "correct": False, "won": False, "game_over": False
            }

        # حساب النتيجة
        score = self.calculate_compatibility(name1, name2)
        message = self.get_compatibility_message(score)
        color = self.get_color(score)

        self.waiting_for_names = False

        card = self._result_card(name1, name2, score, message, color)

        return {
            "response": card,
            "points": 0,
            "correct": False,
            "won": False,
            "game_over": True
        }

    # ---------------------------------------------------------------------
    # UI Components
    # ---------------------------------------------------------------------
    def _header(self, title: str) -> dict:
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [{"type": "text", "text": title, "weight": "bold",
                          "size": "xl", "color": COLORS["white"], "align": "center"}],
            "backgroundColor": COLORS["primary"],
            "paddingAll": "20px",
            "cornerRadius": "12px"
        }

    def _instruction_block(self) -> dict:
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "اكتب اسمين بالشكل التالي:", "size": "md",
                 "color": COLORS["text_dark"], "wrap": True, "weight": "bold", "align": "center"},
                {"type": "text", "text": "اسم و اسم", "size": "xl",
                 "color": COLORS["primary"], "margin": "md", "weight": "bold", "align": "center"},
            ],
            "margin": "lg"
        }

    def _examples_block(self) -> dict:
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "أمثلة:", "size": "sm", "color": COLORS["text_light"], "weight": "bold"},
                {"type": "text", "text": "الحوت و عبير", "size": "sm", "color": COLORS["text_light"]},
                {"type": "text", "text": "القوس و الدلو", "size": "sm", "color": COLORS["text_light"], "margin": "xs"},
            ],
            "margin": "lg"
        }

    def _result_card(self, n1: str, n2: str, score: int, phrase: str, color: str) -> FlexMessage:
        extra = (
            "علاقة رائعة ومميزة" if score >= 90
            else "علاقة قوية ومتينة" if score >= 75
            else "علاقة جيدة ومستقرة" if score >= 60
            else "علاقة تحتاج بعض الاهتمام"
        )

        return FlexMessage(
            alt_text="نتيجة التوافق",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        self._header("نتيجة التوافق"),
                        {
                            "type": "box", "layout": "vertical",
                            "contents": [{"type": "text",
                                          "text": f"{n1} و {n2}",
                                          "size": "lg", "color": COLORS["text_dark"],
                                          "align": "center", "weight": "bold", "wrap": True}],
                            "margin": "lg"
                        },
                        {"type": "separator", "color": COLORS["border"], "margin": "lg"},

                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box", "layout": "vertical",
                                    "contents": [{"type": "text",
                                                  "text": f"{score}%",
                                                  "size": "5xl", "color": color,
                                                  "weight": "bold", "align": "center"}],
                                    "paddingAll": "20px",
                                    "cornerRadius": "12px",
                                    "backgroundColor": color + "1A"
                                },
                                {"type": "text", "text": phrase, "size": "xl",
                                 "color": color, "weight": "bold", "align": "center", "margin": "lg"},
                                {"type": "text", "text": extra, "size": "sm",
                                 "color": COLORS["text_light"], "align": "center"}
                            ],
                            "margin": "lg"
                        },

                        {"type": "separator", "color": COLORS["border"], "margin": "lg"},
                        {
                            "type": "box", "layout": "horizontal", "spacing": "sm",
                            "contents": [
                                {"type": "button", "flex": 1,
                                 "style": "primary", "color": COLORS["primary"],
                                 "action": {"type": "message", "label": "إعادة", "text": "توافق"}},
                                {"type": "button", "flex": 1,
                                 "style": "secondary",
                                 "action": {"type": "message", "label": "بداية", "text": "بداية"}}
                            ]
                        }
                    ],
                    "backgroundColor": COLORS["card_bg"],
                    "paddingAll": "20px"
                }
            })
        )

    # هذه اللعبة لا تحتوي أسئلة متعددة
    def next_question(self):
        return None
