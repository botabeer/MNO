import re
from typing import Dict, Any, Optional
from datetime import datetime
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer

class BaseGame:
    def __init__(self, line_bot_api=None, questions_count: int = 5):
        self.line_bot_api = line_bot_api
        self.questions_count = 5
        self.current_question = 0
        self.current_answer = None
        self.previous_question = None
        self.previous_answer = None
        self.scores: Dict[str, Dict[str, Any]] = {}
        self.answered_users = set()
        self.game_active = False
        self.game_start_time: Optional[datetime] = None
        
        self.game_name = "لعبة"
        self.supports_hint = True
        self.supports_reveal = True
    
    def get_theme_colors(self):
        """الحصول على الوان الثيم"""
        return {
            'primary': '#6B9BD1',
            'success': '#52C5B6',
            'warning': '#F39C6B',
            'error': '#E17B7B',
            'white': '#FFFFFF',
            'text': '#2C3E50',
            'text2': '#7F8C8D',
            'text3': '#95A5A6',
            'border': '#E8ECEF',
            'bg': '#F9FAFB',
            'card': '#FFFFFF'
        }
    
    def normalize_text(self, text: str) -> str:
        """تطبيع النص العربي"""
        if not text:
            return ""
        
        text = text.strip().lower()
        
        replacements = {
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
            'ى': 'ي', 'ة': 'ه', 'ؤ': 'و',
            'ئ': 'ي', 'ء': ''
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        
        return text
    
    def add_score(self, user_id: str, display_name: str, points: int = 1) -> int:
        """اضافة نقاط للاعب"""
        if user_id in self.answered_users:
            return 0
        
        if user_id not in self.scores:
            self.scores[user_id] = {"name": display_name, "score": 0}
        
        self.scores[user_id]["score"] += points
        self.answered_users.add(user_id)
        
        return points
    
    def start_game(self):
        """بدء اللعبة"""
        self.current_question = 0
        self.scores.clear()
        self.answered_users.clear()
        self.previous_question = None
        self.previous_answer = None
        self.game_active = True
        self.game_start_time = datetime.now()
        
        return self.get_question()
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        raise NotImplementedError("يجب تنفيذ get_question في الفئة الفرعية")
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        """التحقق من الاجابة"""
        raise NotImplementedError("يجب تنفيذ check_answer في الفئة الفرعية")
    
    def move_to_next_question(self):
        """الانتقال للسؤال التالي"""
        self.current_question += 1
        self.answered_users.clear()
        
        if self.current_question >= self.questions_count:
            return None
        
        return self.get_question()
    
    def end_game(self) -> Dict[str, Any]:
        """انهاء اللعبة واعلان الفائز"""
        self.game_active = False
        
        if not self.scores:
            message = "انتهت اللعبة - لا يوجد فائز"
            return {
                "game_over": True,
                "points": 0,
                "message": message,
                "response": self.build_winner_flex(None, [])
            }
        
        sorted_players = sorted(
            self.scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        winner = sorted_players[0][1]
        winner_id = sorted_players[0][0]
        
        return {
            "game_over": True,
            "points": winner["score"],
            "winner_id": winner_id,
            "message": f"فاز {winner['name']} بـ {winner['score']} نقطة",
            "response": self.build_winner_flex(winner, sorted_players)
        }
    
    def build_text_message(self, text: str):
        """بناء رسالة نصية"""
        return TextMessage(text=text)
    
    def build_question_message(self, question_text: str, additional_info: str = None):
        """بناء رسالة السؤال Flex"""
        c = self.get_theme_colors()
        progress = f"السؤال {self.current_question + 1} من {self.questions_count}"
        
        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": self.game_name,
                    "size": "xl",
                    "weight": "bold",
                    "color": c["white"],
                    "align": "center"
                }],
                "backgroundColor": c["primary"],
                "paddingAll": "15px",
                "cornerRadius": "10px"
            },
            {
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {"type": "text", "text": f"{self.current_question + 1}", "size": "sm", "color": c["text3"], "flex": 0},
                    {"type": "text", "text": f"من {self.questions_count}", "size": "sm", "color": c["text3"], "align": "end", "flex": 1}
                ],
                "margin": "md"
            },
            {"type": "separator", "margin": "md", "color": c["border"]},
            {
                "type": "text",
                "text": question_text,
                "size": "md",
                "color": c["text"],
                "wrap": True,
                "align": "center",
                "margin": "lg",
                "weight": "bold"
            }
        ]
        
        if additional_info:
            contents.append({
                "type": "text",
                "text": additional_info,
                "size": "sm",
                "color": c["text2"],
                "wrap": True,
                "align": "center",
                "margin": "sm"
            })
        
        if self.previous_question and self.previous_answer:
            prev_ans = (
                self.previous_answer
                if isinstance(self.previous_answer, str)
                else self.previous_answer[0]
            )
            contents.append({"type": "separator", "margin": "md", "color": c["border"]})
            contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "السؤال السابق:", "size": "xs", "color": c["text3"]},
                    {"type": "text", "text": self.previous_question, "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"},
                    {"type": "text", "text": f"الاجابة: {prev_ans}", "size": "xs", "color": c["success"], "wrap": True, "margin": "xs"}
                ],
                "margin": "md"
            })
        
        if self.supports_hint and self.supports_reveal:
            contents.append({"type": "separator", "margin": "md", "color": c["border"]})
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "لمح", "text": "لمح"},
                        "style": "secondary",
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "جاوب", "text": "جاوب"},
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "margin": "md"
            })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": contents,
                "backgroundColor": c["card"],
                "paddingAll": "18px"
            }
        }
        
        return FlexMessage(alt_text=self.game_name, contents=FlexContainer.from_dict(bubble))
    
    def build_winner_flex(self, winner, sorted_players):
        """بناء بطاقة الفائز Flex"""
        c = self.get_theme_colors()
        
        if not winner:
            contents = [
                {"type": "text", "text": "انتهت اللعبة", "size": "xl", "weight": "bold", "color": c["text"], "align": "center"},
                {"type": "text", "text": "لا يوجد فائز", "size": "md", "color": c["text3"], "align": "center", "margin": "md"}
            ]
        else:
            contents = [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [{
                        "type": "text",
                        "text": f"نتائج {self.game_name}",
                        "weight": "bold",
                        "size": "xl",
                        "color": c["white"],
                        "align": "center"
                    }],
                    "backgroundColor": c["primary"],
                    "paddingAll": "12px",
                    "cornerRadius": "8px"
                },
                {
                    "type": "text",
                    "text": f"الفائز: {winner['name']}",
                    "size": "lg",
                    "weight": "bold",
                    "align": "center",
                    "color": c["success"],
                    "margin": "lg"
                },
                {
                    "type": "text",
                    "text": f"النقاط: {winner['score']}",
                    "size": "md",
                    "align": "center",
                    "color": c["text"],
                    "margin": "sm"
                },
                {"type": "separator", "margin": "md", "color": c["border"]}
            ]
            
            for i, (uid, p) in enumerate(sorted_players[:5], 1):
                contents.append({
                    "type": "text",
                    "text": f"{i}. {p['name']} - {p['score']} نقطة",
                    "size": "xs",
                    "color": c["text"],
                    "margin": "sm"
                })
        
        contents.append({"type": "separator", "margin": "md", "color": c["border"]})
        contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "message", "label": "اعادة", "text": self.game_name},
                    "style": "primary",
                    "color": c["primary"],
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
        })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": contents,
                "backgroundColor": c["card"],
                "paddingAll": "16px"
            }
        }
        
        return FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(bubble))
