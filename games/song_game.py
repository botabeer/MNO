# song_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_hint_text

SONGS = [
 {'lyrics':'رجعت لي أيام الماضي معاك','singer':'أم كلثوم'},
 {'lyrics':'تملي معاك ولو حتى بعيد عني','singer':'عمرو دياب'},
 {'lyrics':'يا بنات يا بنات','singer':'نانسي عجرم'},
 # ... إضافات حسب الملف
]

class SongGame:
    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.songs = SONGS
        self.questions = []
        self.current_question = 0
        self.total_questions = total_questions
        self.player_scores = {}
        self.question_answered = False
        self.registered = set()

    def register_player(self, uid, name):
        self.registered.add(uid)

    def start_game(self):
        self.questions = random.sample(self.songs, min(self.total_questions,len(self.songs)))
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        return self._show_question()

    def _show_question(self):
        song = self.questions[self.current_question]
        progress = f"{self.current_question+1}/{self.total_questions}"
        return FlexMessage(alt_text="لعبة الأغنية", contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":[
                {"type":"box","layout":"vertical","contents":[{"type":"text","text":"لعبة الأغنية","weight":"bold","size":"xl","color":COLORS['white']}],"backgroundColor":COLORS['primary'],"paddingAll":"12px","cornerRadius":"10px"},
                {"type":"box","layout":"baseline","contents":[{"type":"text","text":"السؤال","size":"xs","color":COLORS['text_light']},{"type":"text","text":progress,"size":"xs","color":COLORS['primary'],"weight":"bold"}],"margin":"lg"},
                {"type":"separator","margin":"md","color":COLORS['border']},
                {"type":"text","text":song['lyrics'],"size":"lg","weight":"bold","color":COLORS['text_dark'],"align":"center","wrap":True,"margin":"lg"},
                {"type":"separator","margin":"lg","color":COLORS['border']},
                {"type":"box","layout":"horizontal","contents":[{"type":"button","action":{"type":"message","label":"لمح","text":"لمح"},"style":"secondary"},{"type":"button","action":{"type":"message","label":"جاوب","text":"جاوب"},"style":"secondary"}],"spacing":"sm","margin":"lg"}
            ], "backgroundColor":COLORS['card_bg'],"paddingAll":"16px"}}
        ))

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.question_answered = False
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        if user_id not in self.registered:
            return None
        song = self.questions[self.current_question]
        txt = answer.strip().lower()
        if txt in ['لمح','تلميح']:
            hint = create_hint_text(song['singer'])
            return {'response': TextMessage(text=hint), 'points':0, 'correct':False}
        if txt in ['جاوب','الجواب','الحل']:
            self.question_answered = True
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"الإجابة: {song['singer']}"), 'points':0, 'correct':False, 'next_question':True}
            return self._end_game()
        if self.question_answered:
            return None
        if normalize_text(answer) == normalize_text(song['singer']):
            self.player_scores.setdefault(user_id, {'name':display_name,'score':0})
            self.player_scores[user_id]['score'] += 1
            self.question_answered = True
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"إجابة صحيحة {display_name}\n+1 نقطة"), 'points':1, 'correct':True, 'next_question':True}
            return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة بدون فائز"), 'points':0, 'game_over':True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x:x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        players_contents = []
        for i,p in enumerate(sorted_players[:5]):
            players_contents.append({"type":"text","text":f"{i+1}. {p[1]['name']} - {p[1]['score']}","size":"sm","color":COLORS['text_dark']})
        winner_card = FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":[
                {"type":"box","layout":"vertical","contents":[{"type":"text","text":"انتهت اللعبة","weight":"bold","size":"xl","color":COLORS['white'] }],"backgroundColor":COLORS['primary'],"paddingAll":"12px","cornerRadius":"10px"},
                {"type":"text","text":f"الفائز: {winner['name']} - {winner['score']} نقطة","size":"md","color":COLORS['text_dark']},
                {"type":"separator","margin":"md","color":COLORS['border']},
                *players_contents
            ], "backgroundColor":COLORS['card_bg'],"paddingAll":"16px"}}
        ))
        return {'response': winner_card, 'points': winner['score'], 'game_over':True}
