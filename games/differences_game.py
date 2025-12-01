from linebot.models import TextSendMessage, ImageSendMessage, FlexSendMessage
import random

COLORS = {
    'primary': '#00D4FF',
    'dark': '#1A1A2E',
    'card_bg': '#1E2A38',
    'text_light': '#8FA3B8',
    'text_dark': '#E8EEF3',
    'border': '#2D3E50'
}

class DifferencesGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.image_pairs = [
            {
                "original": "https://up6.cc/2025/10/176308448198881.jpeg",
                "solution": "https://mrkzgulfup.com/uploads/176303338684742.jpeg",
                "differences": 5
            },
            {
                "original": "https://up6.cc/2025/10/176308448205332.jpeg",
                "solution": "https://mrkzgulfup.com/uploads/176303338695684.jpeg",
                "differences": 5
            },
            {
                "original": "https://up6.cc/2025/10/176308448209753.jpeg",
                "solution": "https://mrkzgulfup.com/uploads/176303338714356.jpeg",
                "differences": 5
            },
            {
                "original": "https://up6.cc/2025/10/17630844821154.jpeg",
                "solution": "https://mrkzgulfup.com/uploads/176303338717158.jpeg",
                "differences": 5
            },
            {
                "original": "https://up6.cc/2025/10/176308448213085.jpeg",
                "solution": "https://mrkzgulfup.com/uploads/1763033387284912.jpeg",
                "differences": 5
            }
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()
    
    def start_game(self):
        self.questions = random.sample(self.image_pairs, min(self.total_questions, len(self.image_pairs)))
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()
    
    def _show_question(self):
        pair = self.questions[self.current_question]
        
        card = FlexSendMessage(
            alt_text="لعبة الاختلافات",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "لعبة الاختلافات",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#FFFFFF"
                                }
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"صورة {self.current_question + 1} من {self.total_questions}",
                                    "size": "sm",
                                    "color": COLORS['text_light']
                                },
                                {
                                    "type": "text",
                                    "text": f"ابحث عن {pair['differences']} اختلافات",
                                    "size": "lg",
                                    "color": COLORS['text_dark'],
                                    "weight": "bold",
                                    "margin": "md"
                                }
                            ],
                            "margin": "lg",
                            "spacing": "sm"
                        },
                        {
                            "type": "separator",
                            "margin": "lg",
                            "color": COLORS['border']
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "جاوب - عرض الحل", "text": "جاوب"},
                            "style": "secondary",
                            "height": "sm",
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        
        image = ImageSendMessage(
            original_content_url=pair['original'],
            preview_image_url=pair['original']
        )
        
        return [card, image]
    
    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            return self._show_question()
        return None
    
    def check_answer(self, answer, user_id, display_name):
        if user_id in self.answered_users:
            return None
        
        answer_lower = answer.strip().lower()
        
        if answer_lower in ['جاوب', 'الجواب', 'الحل']:
            pair = self.questions[self.current_question]
            self.answered_users.add(user_id)
            
            solution_image = ImageSendMessage(
                original_content_url=pair['solution'],
                preview_image_url=pair['solution']
            )
            
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': [TextSendMessage(text="الحل:"), solution_image],
                    'points': 0,
                    'correct': False,
                    'next_question': True
                }
            else:
                return self._end_game_with_solution(solution_image)
        
        return None
    
    def _end_game_with_solution(self, solution_image):
        winner_card = FlexSendMessage(
            alt_text="انتهت اللعبة",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "انتهت اللعبة",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#FFFFFF"
                                }
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "تم عرض جميع الصور",
                                    "size": "md",
                                    "color": COLORS['text_dark'],
                                    "align": "center"
                                }
                            ],
                            "margin": "lg"
                        },
                        {
                            "type": "separator",
                            "margin": "lg",
                            "color": COLORS['border']
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "إعادة", "text": "اختلاف"},
                            "style": "primary",
                            "color": COLORS['primary'],
                            "height": "sm",
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        
        return {
            'response': [TextSendMessage(text="الحل:"), solution_image, winner_card],
            'points': 0,
            'correct': False,
            'game_over': True
        }
