"""
تطبيق LINE Bot للألعاب - نسخة احترافية محسّنة
التصميم: أنيق ومريح للعين - أسود، أبيض، رمادي
"""
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from datetime import datetime
from collections import defaultdict
import threading
import logging

# استيراد الأدوات المساعدة
from utils.ui_components import (
    get_welcome_message, get_join_message, get_help_message,
    get_withdrawal_message, get_error_message, get_fixed_quick_reply
)

# استيراد الألعاب
from games.compatibility_game import CompatibilityGame

# ========== إعداد السجلات ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ========== إنشاء التطبيق ==========
app = Flask(__name__)

# ========== إعداد LINE Bot ==========
LINE_CHANNEL_ACCESS_TOKEN = os.getenv(
    "LINE_CHANNEL_ACCESS_TOKEN",
    "YOUR_CHANNEL_ACCESS_TOKEN"
)
LINE_CHANNEL_SECRET = os.getenv(
    "LINE_CHANNEL_SECRET",
    "YOUR_CHANNEL_SECRET"
)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ========== البيانات العامة ==========
active_games = {}
registered_players = set()
player_scores = defaultdict(int)
games_lock = threading.Lock()
players_lock = threading.Lock()

# ========== تهيئة الألعاب ==========
compatibility_game = CompatibilityGame(line_bot_api)

# خريطة الألعاب المتاحة
GAMES_MAP = {
    "توافق": compatibility_game,
    # يمكن إضافة المزيد من الألعاب هنا
}

# ========== الأوامر المتاحة ==========
BASIC_COMMANDS = ["مساعدة", "انضم", "انسحب", "إيقاف", "نقاطي", "الصدارة"]
GAME_COMMANDS = list(GAMES_MAP.keys())
SPECIAL_COMMANDS = ["سؤال", "تحدي", "اعتراف", "اكثر", "لمح", "جاوب"]
ALL_COMMANDS = BASIC_COMMANDS + GAME_COMMANDS + SPECIAL_COMMANDS


# ========== دالة تنظيف البيانات القديمة ==========
def cleanup_old_games():
    """تنظيف الألعاب القديمة كل 30 دقيقة"""
    while True:
        try:
            threading.Event().wait(1800)  # 30 دقيقة
            current_time = datetime.now()
            
            with games_lock:
                expired_games = []
                for game_id, game_data in active_games.items():
                    time_diff = (current_time - game_data["created_at"]).seconds
                    if time_diff > 3600:  # ساعة واحدة
                        expired_games.append(game_id)
                
                for game_id in expired_games:
                    del active_games[game_id]
                    logger.info(f"🧹 تم حذف اللعبة المنتهية: {game_id}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في التنظيف: {e}")


# بدء خيط التنظيف
cleanup_thread = threading.Thread(target=cleanup_old_games, daemon=True)
cleanup_thread.start()


# ========== نقطة استقبال Webhook ==========
@app.route("/callback", methods=["POST"])
def callback():
    """استقبال الرسائل من LINE"""
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    
    logger.info(f"📩 استلام webhook من LINE")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("❌ توقيع غير صالح")
        abort(400)
    
    return "OK"


# ========== معالج الرسائل النصية ==========
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """معالجة الرسائل النصية الواردة"""
    try:
        user_text = event.message.text.strip()
        user_id = event.source.user_id
        
        # تجاهل الرسائل الفارغة
        if not user_text:
            return
        
        logger.info(f"📨 رسالة من {user_id}: {user_text}")
        
        # ========== معالجة الأوامر الأساسية ==========
        
        # أمر المساعدة
        if user_text == "مساعدة":
            line_bot_api.reply_message(event.reply_token, get_help_message())
            logger.info("✅ تم إرسال رسالة المساعدة")
            return
        
        # أمر الانضمام
        if user_text == "انضم":
            with players_lock:
                registered_players.add(user_id)
            
            # الحصول على اسم المستخدم
            try:
                profile = line_bot_api.get_profile(user_id)
                username = profile.display_name
            except Exception:
                username = "مستخدم"
            
            line_bot_api.reply_message(event.reply_token, get_join_message(username))
            logger.info(f"✅ انضم اللاعب: {username} ({user_id})")
            return
        
        # أمر الانسحاب
        if user_text == "انسحب":
            with players_lock:
                if user_id in registered_players:
                    registered_players.remove(user_id)
            
            try:
                profile = line_bot_api.get_profile(user_id)
                username = profile.display_name
            except Exception:
                username = "مستخدم"
            
            line_bot_api.reply_message(event.reply_token, get_withdrawal_message(username))
            logger.info(f"✅ انسحب اللاعب: {username} ({user_id})")
            return
        
        # أمر إيقاف اللعبة
        if user_text == "إيقاف":
            with games_lock:
                user_games = [gid for gid, gdata in active_games.items() 
                             if user_id in gdata.get("participants", set())]
                for game_id in user_games:
                    del active_games[game_id]
            
            msg = "⏹️ تم إيقاف اللعبة الحالية بنجاح."
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=msg, quick_reply=get_fixed_quick_reply())
            )
            logger.info(f"✅ تم إيقاف اللعبة للمستخدم: {user_id}")
            return
        
        # أمر عرض النقاط
        if user_text == "نقاطي":
            score = player_scores.get(user_id, 0)
            msg = f"📊 نقاطك الحالية: {score} نقطة\n\nاستمر في اللعب لزيادة نقاطك! 💪"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=msg, quick_reply=get_fixed_quick_reply())
            )
            return
        
        # أمر قائمة الصدارة
        if user_text == "الصدارة":
            sorted_scores = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)
            
            if not sorted_scores:
                msg = "🏆 قائمة الصدارة\n\nلا توجد نقاط مسجلة بعد.\nكن أول من يسجل!"
            else:
                msg = "🏆 قائمة الصدارة\n\n═══════════════════\n\n"
                medals = ["🥇", "🥈", "🥉"]
                
                for idx, (uid, score) in enumerate(sorted_scores[:10], 1):
                    try:
                        profile = line_bot_api.get_profile(uid)
                        name = profile.display_name
                    except Exception:
                        name = f"لاعب {idx}"
                    
                    medal = medals[idx-1] if idx <= 3 else f"{idx}."
                    msg += f"{medal} {name} - {score} نقطة\n"
                
                msg += "\n═══════════════════"
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=msg, quick_reply=get_fixed_quick_reply())
            )
            return
        
        # ========== معالجة بدء الألعاب ==========
        
        if user_text in GAME_COMMANDS:
            game = GAMES_MAP[user_text]
            
            # إنشاء معرف فريد للعبة
            game_id = f"{user_id}_{user_text}_{datetime.now().strftime('%H%M%S')}"
            
            # إضافة اللعبة للألعاب النشطة
            with games_lock:
                active_games[game_id] = {
                    "game": game,
                    "type": user_text,
                    "created_at": datetime.now(),
                    "participants": {user_id}
                }
            
            # بدء اللعبة
            response = game.start_game()
            line_bot_api.reply_message(event.reply_token, response)
            logger.info(f"🎮 بدأت لعبة {user_text} - {game_id}")
            return
        
        # ========== معالجة مدخلات اللعبة ==========
        
        # التحقق من وجود لعبة نشطة للمستخدم
        with games_lock:
            user_game = None
            for game_id, game_data in active_games.items():
                if user_id in game_data.get("participants", set()):
                    user_game = game_data
                    break
        
        if user_game and user_game["type"] == "توافق":
            compatibility_game.process_input(event)
            return
        
        # ========== الأوامر الخاصة ==========
        
        if user_text in SPECIAL_COMMANDS:
            special_messages = {
                "سؤال": "❓ سؤال عشوائي قادم...",
                "تحدي": "🎯 تحدي جديد في الطريق...",
                "اعتراف": "💭 اعتراف مثير للاهتمام...",
                "اكثر": "➕ المزيد من الخيارات...",
                "لمح": "💡 تلميح: استخدم الأزرار السريعة!",
                "جاوب": "✅ الإجابة الصحيحة..."
            }
            
            msg = special_messages.get(user_text, "قيد التنفيذ...")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=msg, quick_reply=get_fixed_quick_reply())
            )
            return
        
        # ========== رسالة افتراضية ==========
        
        # إذا كان النص غير معروف، نتجاهله أو نرسل رسالة ترحيب
        if user_text.startswith("/") or user_text in ["start", "بدء"]:
            try:
                profile = line_bot_api.get_profile(user_id)
                username = profile.display_name
            except Exception:
                username = "مستخدم"
            
            line_bot_api.reply_message(event.reply_token, get_welcome_message(username))
            return
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}", exc_info=True)
        try:
            error_msg = "⚠️ حدث خطأ في معالجة رسالتك. حاول مرة أخرى."
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=error_msg, quick_reply=get_fixed_quick_reply())
            )
        except Exception:
            pass


# ========== صفحة الحالة ==========
@app.route("/", methods=["GET"])
def home():
    """صفحة الحالة الرئيسية"""
    return {
        "status": "running",
        "bot_name": "LINE Games Bot",
        "version": "2.0",
        "active_games": len(active_games),
        "registered_players": len(registered_players)
    }


# ========== صفحة الصحة ==========
@app.route("/health", methods=["GET"])
def health():
    """فحص صحة التطبيق"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ========== تشغيل التطبيق ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    logger.info("═══════════════════════════════════")
    logger.info("🚀 بدء تشغيل LINE Games Bot")
    logger.info(f"📡 المنفذ: {port}")
    logger.info(f"🎮 الألعاب المتاحة: {len(GAMES_MAP)}")
    logger.info(f"📊 اللاعبون المسجلون: {len(registered_players)}")
    logger.info(f"🎯 الألعاب النشطة: {len(active_games)}")
    logger.info("═══════════════════════════════════")
    
    app.run(host="0.0.0.0", port=port, debug=False)
