import random
from linebot.models import TextSendMessage
from utils.ui_components import get_name_compatibility_message

class CompatibilityGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.user_states = {}  # user_id -> waiting for names

    def start(self, event):
        user_id = event.source.user_id
        self.user_states[user_id] = "waiting_for_names"
        reply = TextSendMessage(
            text="✨ أرسل اسمين مفصولين بمسافة مثل:\n\nخالد سارة"
        )
        self.line_bot_api.reply_message(event.reply_token, reply)

    def handle_response(self, event, text):
        user_id = event.source.user_id
        if self.user_states.get(user_id) != "waiting_for_names":
            return False

        parts = text.split()
        if len(parts) == 2:
            name1, name2 = parts
            percentage = (sum(ord(c) for c in name1 + name2) % 100)
            reply = get_name_compatibility_message(name1, name2, percentage)
            self.line_bot_api.reply_message(event.reply_token, reply)
            del self.user_states[user_id]
        else:
            reply = TextSendMessage(text="❗ الرجاء إدخال اسمين فقط، مثال:\n\nأحمد ريم")
            self.line_bot_api.reply_message(event.reply_token, reply)
        return True
