"""
ملف مكونات واجهة المستخدم - تصميم أنيق ومريح للعين
الألوان: أسود، أبيض، رمادي
"""
from linebot.models import (
    FlexSendMessage, BubbleContainer, BoxComponent, TextComponent,
    QuickReply, QuickReplyButton, MessageAction, SeparatorComponent
)

# ========== نظام الألوان الأنيق ==========
COLOR_PRIMARY = "#000000"      # أسود نقي للعناوين
COLOR_SECONDARY = "#6B6B6B"    # رمادي متوسط للنصوص الثانوية
COLOR_ACCENT = "#9E9E9E"       # رمادي فاتح للتفاصيل
COLOR_BG = "#FFFFFF"           # خلفية بيضاء نقية
COLOR_BORDER = "#E0E0E0"       # حدود رمادية فاتحة جداً
COLOR_SUCCESS = "#2C2C2C"      # أسود داكن للنجاح
COLOR_ERROR = "#4A4A4A"        # رمادي داكن للأخطاء

# ========== الأزرار الثابتة ==========
def get_fixed_quick_reply():
    """إرجاع الأزرار الثابتة بتصميم منظم"""
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="🎵 أغنية", text="أغنية")),
        QuickReplyButton(action=MessageAction(label="🎮 لعبة", text="لعبة")),
        QuickReplyButton(action=MessageAction(label="⛓️ سلسلة", text="سلسلة")),
        QuickReplyButton(action=MessageAction(label="⚡ أسرع", text="أسرع")),
        QuickReplyButton(action=MessageAction(label="🔄 ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="📝 ترتيب", text="ترتيب")),
        QuickReplyButton(action=MessageAction(label="🔤 كوّن", text="كوّن")),
        QuickReplyButton(action=MessageAction(label="🔍 اختلاف", text="اختلاف")),
        QuickReplyButton(action=MessageAction(label="💞 توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="❓ سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="🎯 تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="💭 اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="➕ اكثر", text="اكثر"))
    ])

# ========== إنشاء رسائل Flex أنيقة ==========
def create_elegant_flex_message(title, body, emoji="", show_separator=True):
    """
    إنشاء رسالة Flex بتصميم أنيق واحترافي
    
    Args:
        title: عنوان الرسالة
        body: محتوى الرسالة
        emoji: إيموجي اختياري للعنوان
        show_separator: إظهار خط فاصل
    """
    contents = [
        TextComponent(
            text=f"{emoji} {title}" if emoji else title,
            weight="bold",
            size="xl",
            color=COLOR_PRIMARY,
            wrap=True
        )
    ]
    
    if show_separator:
        contents.append(
            SeparatorComponent(margin="md", color=COLOR_BORDER)
        )
    
    contents.append(
        TextComponent(
            text=body,
            wrap=True,
            color=COLOR_SECONDARY,
            size="md",
            margin="md",
            line_height="1.6"
        )
    )
    
    bubble = BubbleContainer(
        direction="ltr",
        body=BoxComponent(
            layout="vertical",
            spacing="sm",
            contents=contents,
            background_color=COLOR_BG,
            padding_all="16px"
        )
    )
    
    return FlexSendMessage(
        alt_text=title,
        contents=bubble,
        quick_reply=get_fixed_quick_reply()
    )

# ========== رسائل الترحيب ==========
def get_welcome_message(display_name):
    """رسالة ترحيب أنيقة للمستخدمين الجدد"""
    title = f"مرحباً {display_name}"
    body = (
        "أهلاً بك في عالم الألعاب المميز! 🎮\n\n"
        "استخدم الأزرار أدناه للبدء في أي لعبة، "
        "أو اكتب 'مساعدة' لعرض جميع الأوامر المتاحة.\n\n"
        "استمتع بوقتك! ✨"
    )
    return create_elegant_flex_message(title, body, emoji="👋", show_separator=True)

# ========== رسائل المساعدة ==========
def get_help_message():
    """رسالة المساعدة الشاملة"""
    title = "دليل الاستخدام"
    body = (
        "═══ الأوامر الأساسية ═══\n\n"
        "• مساعدة - عرض هذه القائمة\n"
        "• انضم - التسجيل للعب\n"
        "• انسحب - الخروج من اللعبة\n"
        "• إيقاف - إنهاء اللعبة الحالية\n\n"
        "═══ أوامر المعلومات ═══\n\n"
        "• نقاطي - عرض نقاطك\n"
        "• الصدارة - قائمة أفضل اللاعبين\n\n"
        "═══ الألعاب المتاحة ═══\n\n"
        "استخدم الأزرار الثابتة أدناه لبدء أي لعبة:\n"
        "🎵 أغنية • 🎮 لعبة • ⛓️ سلسلة\n"
        "⚡ أسرع • 🔄 ضد • 📝 ترتيب\n"
        "🔤 كوّن • 🔍 اختلاف • 💞 توافق\n\n"
        "═══ أوامر إضافية ═══\n\n"
        "❓ سؤال • 🎯 تحدي • 💭 اعتراف • ➕ اكثر"
    )
    return create_elegant_flex_message(title, body, emoji="📖", show_separator=True)

# ========== رسالة الانضمام ==========
def get_join_message(display_name):
    """رسالة تأكيد الانضمام"""
    title = "تم التسجيل بنجاح"
    body = (
        f"مرحباً {display_name}! ✨\n\n"
        "لقد تم تسجيلك بنجاح في نظام الألعاب.\n\n"
        "الآن يمكنك المشاركة في جميع الألعاب المتاحة "
        "باستخدام الأزرار أدناه.\n\n"
        "نتمنى لك أوقاتاً ممتعة! 🎮"
    )
    return create_elegant_flex_message(title, body, emoji="✅", show_separator=True)

# ========== رسالة الانسحاب ==========
def get_withdrawal_message(display_name):
    """رسالة تأكيد الانسحاب"""
    title = "تم الانسحاب"
    body = (
        f"وداعاً {display_name}! 👋\n\n"
        "لقد تم انسحابك من اللعبة الحالية.\n\n"
        "يمكنك الانضمام مجدداً في أي وقت "
        "باستخدام زر 'انضم'.\n\n"
        "نتطلع لرؤيتك قريباً!"
    )
    return create_elegant_flex_message(title, body, emoji="👋", show_separator=True)

# ========== رسائل الأخطاء ==========
def get_error_message(error_text):
    """رسالة خطأ أنيقة"""
    title = "تنبيه"
    return create_elegant_flex_message(title, error_text, emoji="⚠️", show_separator=True)

# ========== رسائل النجاح ==========
def get_success_message(success_text):
    """رسالة نجاح أنيقة"""
    title = "عمل رائع"
    return create_elegant_flex_message(title, success_text, emoji="🎉", show_separator=True)

# ========== رسالة قائمة الصدارة ==========
def get_leaderboard_message(top_players):
    """
    رسالة قائمة الصدارة
    
    Args:
        top_players: قائمة بالمستخدمين وأعلى النقاط [(name, score), ...]
    """
    title = "قائمة الصدارة"
    
    if not top_players:
        body = "لا توجد نقاط مسجلة بعد.\nكن أول من يسجل نقاطاً! 🏆"
    else:
        medals = ["🥇", "🥈", "🥉"]
        body = "═══ أفضل اللاعبين ═══\n\n"
        
        for idx, (name, score) in enumerate(top_players[:10], 1):
            medal = medals[idx-1] if idx <= 3 else f"{idx}."
            body += f"{medal} {name} - {score} نقطة\n"
    
    return create_elegant_flex_message(title, body, emoji="🏆", show_separator=True)

# ========== رسالة النقاط الشخصية ==========
def get_personal_score_message(display_name, score, rank=None):
    """
    رسالة عرض النقاط الشخصية
    
    Args:
        display_name: اسم اللاعب
        score: النقاط
        rank: الترتيب (اختياري)
    """
    title = "نقاطك الشخصية"
    
    rank_text = f"\nترتيبك: #{rank}" if rank else ""
    body = (
        f"اللاعب: {display_name}\n"
        f"النقاط: {score} نقطة{rank_text}\n\n"
        "استمر في اللعب لزيادة نقاطك! 💪"
    )
    
    return create_elegant_flex_message(title, body, emoji="📊", show_separator=True)
