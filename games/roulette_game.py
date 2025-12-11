"""
لعبة روليت - Bot Mesh v22.2 PRO 3D
Created by: Abeer Aldosari © 2025
نقطة واحدة لكل فوز | ثيمات | سؤال سابق | أزرار | بدون وقت
"""

from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional


class RouletteGame(BaseGame):
    """لعبة روليت"""

    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "روليت"
        self.supports_hint = True
        self.supports_reveal = True

        self.roulette_numbers = list(range(0, 37))
        
        self.red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        self.black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        
        self.current_spin_result = None
        self.last_spin_result = None

    def start_game(self):
        self.current_question = 0
        self.game_active = True
        self.previous_question = None
        self.previous_answer = None
        self.answered_users.clear()
        self.scores.clear()
        return self.get_question()

    def spin_roulette(self):
        """تدوير الروليت"""
        return random.choice(self.roulette_numbers)

    def get_color(self, number: int) -> str:
        """الحصول على لون الرقم"""
        if number == 0:
            return "أخضر"
        elif number in self.red_numbers:
            return "أحمر"
        else:
            return "أسود"

    def get_question(self):
        """إنشاء سؤال الروليت"""
        self.current_spin_result = self.spin_roulette()
        result_color = self.get_color(self.current_spin_result)
        
        c = self.get_theme_colors()
        
        color_display = {
            "أحمر": "#DC2626",
            "أسود": "#1F2937",
            "أخضر": "#059669"
        }
        
        display_color = color_display.get(result_color, c["primary"])
        
        progress_percent = int(((self.current_question + 1) / self.questions_count) * 100)
        progress_text = f"الجولة {self.current_question + 1}/{self.questions_count}"
        
        contents = [
            {
                "type": "text",
                "text": self.game_name,
                "size": "xxl",
                "weight": "bold",
                "color": c["primary"],
                "align": "center"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": progress_text,
                                "size": "xs",
                                "color": c["text2"],
                                "flex": 1
                            },
                            {
                                "type": "text",
                                "text": f"{progress_percent}%",
                                "size": "xs",
                                "color": c["primary"],
                                "weight": "bold",
                                "align": "end",
                                "flex": 0
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "width": f"{progress_percent}%",
                                "backgroundColor": c["primary"],
                                "height": "6px",
                                "cornerRadius": "3px"
                            }
                        ],
                        "backgroundColor": c["border"],
                        "height": "6px",
                        "cornerRadius": "3px",
                        "margin": "sm"
                    }
                ],
                "margin": "md"
            },
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        if self.last_spin_result is not None:
            last_color = self.get_color(self.last_spin_result)
            contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "الدورة السابقة",
                        "size": "xs",
                        "color": c["text3"],
                        "weight": "bold"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"الرقم: {self.last_spin_result}",
                                "size": "xs",
                                "color": c["text2"],
                                "flex": 1
                            },
                            {
                                "type": "text",
                                "text": last_color,
                                "size": "xs",
                                "color": color_display.get(last_color, c["text2"]),
                                "weight": "bold",
                                "flex": 0
                            }
                        ],
                        "margin": "xs"
                    }
                ],
                "backgroundColor": c["card"],
                "cornerRadius": "12px",
                "paddingAll": "12px",
                "borderWidth": "1px",
                "borderColor": c["border"],
                "margin": "md"
            })
            contents.append({"type": "separator", "margin": "lg", "color": c["border"]})
        
        contents.append({
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "تدور الروليت",
                    "size": "md",
                    "color": c["text2"],
                    "align": "center",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": str(self.current_spin_result),
                            "size": "xxl",
                            "weight": "bold",
                            "color": display_color,
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": result_color,
                            "size": "lg",
                            "weight": "bold",
                            "color": display_color,
                            "align": "center",
                            "margin": "sm"
                        }
                    ],
                    "backgroundColor": c["card"],
                    "cornerRadius": "50px",
                    "paddingAll": "30px",
                    "borderWidth": "3px",
                    "borderColor": display_color,
                    "margin": "lg"
                },
                {
                    "type": "text",
                    "text": "خمن ماذا سيكون",
                    "size": "sm",
                    "color": c["text2"],
                    "align": "center",
                    "margin": "lg"
                }
            ]
        })
        
        contents.extend([
            {"type": "separator", "margin": "xl", "color": c["border"]},
            {
                "type": "text",
                "text": "خيارات الرهان",
                "size": "sm",
                "weight": "bold",
                "color": c["text"],
                "align": "center",
                "margin": "md"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "رقم محدد: اكتب الرقم من 0-36",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "لون: اكتب أحمر أو أسود",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": "زوجي/فردي: اكتب زوجي أو فردي",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": "نطاق: 1-18 أو 19-36",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "xs"
                    }
                ],
                "backgroundColor": c["info_bg"],
                "cornerRadius": "12px",
                "paddingAll": "12px",
                "margin": "sm"
            }
        ])
        
        if self.can_use_hint() and self.can_reveal_answer():
            contents.extend([
                {"type": "separator", "margin": "xl", "color": c["border"]},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "margin": "lg",
                    "contents": [
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "لمح", "text": "لمح"},
                            "style": "secondary",
                            "height": "sm",
                            "color": c["secondary"]
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "جاوب", "text": "جاوب"},
                            "style": "secondary",
                            "height": "sm",
                            "color": c["secondary"]
                        }
                    ]
                }
            ])
        
        return self._create_flex_with_buttons(
            self.game_name,
            {
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": contents,
                    "paddingAll": "24px",
                    "backgroundColor": c["bg"]
                }
            }
        )

    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active or user_id in self.answered_users:
            return None

        if self.team_mode and user_id not in self.joined_users:
            return None

        normalized = self.normalize_text(user_answer)

        if self.can_use_hint() and normalized == "لمح":
            result_color = self.get_color(self.current_spin_result)
            is_even = self.current_spin_result % 2 == 0 and self.current_spin_result != 0
            hint = f"اللون: {result_color}\n"
            hint += "زوجي" if is_even else "فردي" if self.current_spin_result != 0 else "صفر"
            return {"message": hint, "response": self._create_text_message(hint), "points": 0}

        if self.can_reveal_answer() and normalized == "جاوب":
            reveal = f"الرقم: {self.current_spin_result}\nاللون: {self.get_color(self.current_spin_result)}"
            self.previous_question = "تخمين الروليت"
            self.previous_answer = reveal
            self.last_spin_result = self.current_spin_result
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"{reveal}\n\n{result.get('message', '')}"
                return result

            return {"message": reveal, "response": self.get_question(), "points": 0}

        if self.team_mode and normalized in ["لمح", "جاوب"]:
            return None

        won = False
        win_type = ""
        
        try:
            guess_number = int(user_answer.strip())
            if 0 <= guess_number <= 36 and guess_number == self.current_spin_result:
                won = True
                win_type = "رقم مباشر"
        except ValueError:
            pass
        
        if not won:
            result_color = self.get_color(self.current_spin_result)
            if normalized in ["احمر", "اسود"]:
                if (normalized == "احمر" and result_color == "أحمر") or \
                   (normalized == "اسود" and result_color == "أسود"):
                    won = True
                    win_type = "لون"
        
        if not won and self.current_spin_result != 0:
            is_even = self.current_spin_result % 2 == 0
            if (normalized == "زوجي" and is_even) or (normalized == "فردي" and not is_even):
                won = True
                win_type = "زوجي/فردي"
        
        if not won:
            if normalized in ["1-18", "منخفض", "صغير"] and 1 <= self.current_spin_result <= 18:
                won = True
                win_type = "نطاق منخفض"
            elif normalized in ["19-36", "مرتفع", "كبير"] and 19 <= self.current_spin_result <= 36:
                won = True
                win_type = "نطاق مرتفع"

        if won:
            total_points = 1

            if self.team_mode:
                team = self.get_user_team(user_id) or self.assign_to_team(user_id)
                self.add_team_score(team, total_points)
            else:
                self.add_score(user_id, display_name, total_points)

            self.previous_question = "تخمين الروليت"
            self.previous_answer = f"{self.current_spin_result} - {self.get_color(self.current_spin_result)}"
            self.last_spin_result = self.current_spin_result
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = total_points
                return result

            return {
                "message": f"صحيح - {win_type} +{total_points}",
                "response": self.get_question(),
                "points": total_points
            }

        return None
