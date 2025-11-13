from linebot.models import (
    FlexSendMessage, BubbleContainer, BoxComponent, TextComponent,
    ButtonComponent, URIAction, QuickReply, QuickReplyButton
)

# 🎨 ألوان أساسية
COLOR_BG = "#F5F5F5"        # خلفية رمادية فاتحة
COLOR_PRIMARY = "#000000"   # أسود للنصوص
COLOR_SECONDARY = "#888888" # رمادي للنصوص الثانوية
COLOR_ACCENT = "#FFFFFF"    # أبيض للتباين

# ⚙️ الأزرار الثابتة للألعاب
def get_fixed_quick_reply():
    """إرجاع الأزرار الثابتة للألعاب والأوامر الخاصة"""
    return QuickReply(items=[
        QuickReplyButton(action=URIAction(label="أغنية", uri="line://app/أغنية")),
        QuickReplyButton(action=URIAction(label="لعبة", uri="line://app/لعبة")),
        QuickReplyButton(action=URIAction(label="سلسلة", uri="line://app/سلسلة")),
        QuickReplyButton(action=URIAction(label="أسرع", uri="line://app/أسرع")),
        QuickReplyButton(action=URIAction(label="ضد", uri="line://app/ضد")),
        QuickReplyButton(action=URIAction(label="ترتيب", uri="line://app/ترتيب")),
        QuickReplyButton(action=URIAction(label="كوّن", uri="line://app/كوّن")),
        QuickReplyButton(action=URIAction(label="اختلاف", uri="line://app/اختلاف")),
        QuickReplyButton(action=URIAction(label="سؤال", uri="line://app/سؤال")),
        QuickReplyButton(action=URIAction(label="تحدي", uri="line://app/تحدي")),
        QuickReplyButton(action=URIAction(label="اعتراف", uri="line://app/اعتراف")),
        QuickReplyButton(action=URIAction(label="اكثر", uri="line://app/اكثر"))
    ])

# 🧩 إنشاء رسائل Flex موحدة التصميم
def create_flex_text_message(title, body):
    """إنشاء رسالة Flex أنيقة باللونين الأسود والرمادي"""
    bubble = BubbleContainer(
        direction="ltr",
        body=BoxComponent(
            layout="vertical",
            spacing="md",
            contents=[
                TextComponent(text=title, weight="bold", size="lg", color=COLOR_PRIMARY),
                TextComponent(text=body, wrap=True, color=COLOR_SECONDARY, size="md")
            ],
            background_color=COLOR_BG,
            padding_all="12px",
            corner_radius="10px"
        )
    )
    return FlexSendMessage(alt_text=title, contents=bubble)

# 👋 رسالة الترحيب
def get_welcome_message(display_name):
    title = f"مرحباً {display_name} 👋"
    body = "اختر اللعبة التي تريد لعبها من الأزرار أدناه أو استعرض الأوامر."
    return create_flex_text_message(title, body)

# 📜 رسالة المساعدة
def get_help_message():
    title = "📜 قائمة الأوامر المتاحة"
    body = (
        "- مساعدة: عرض قائمة الأوامر\n"
        "- انضم: الانضمام للعب\n"
        "- انسحب: الخروج من اللعبة\n"
        "- إيقاف: إيقاف اللعبة الحالية\n"
        "- نقاطي: عرض نقاطك\n"
        "- الصدارة: عرض قائمة الصدارة\n"
        "- الألعاب: استخدم الأزرار الثابتة لبدء أي لعبة"
    )
    return create_flex_text_message(title, body)

# ✅ عند الانضمام
def get_join_message(display_name):
    title = f"✅ {display_name} تم تسجيلك"
    body = "الآن أنت جاهز للعب، اختر اللعبة من الأزرار أدناه."
    return create_flex_text_message(title, body)

# 📊 إحصائيات المستخدم
def get_stats_message(user_stats):
    title = "📊 إحصائياتك"
    body = f"عدد الألعاب: {user_stats.get('games_played', 0)}\nالنقاط: {user_stats.get('points', 0)}"
    return create_flex_text_message(title, body)

# 🏆 قائمة الصدارة
def get_leaderboard_message(leaderboard):
    title = "🏆 قائمة الصدارة"
    body_lines = [f"{idx+1}. {user['name']} - {user['points']} نقطة" for idx, user in enumerate(leaderboard)]
    body = "\n".join(body_lines)
    return create_flex_text_message(title, body)

# 💞 توافق الأسماء
def get_name_compatibility_message(name1, name2, percentage):
    """إنشاء رسالة توافق بين اسمين بتصميم أنيق"""
    if percentage >= 80:
        desc = "❤️ توافق رائع جدًا!"
    elif percentage >= 60:
        desc = "💞 توافق جميل ومبشر!"
    elif percentage >= 40:
        desc = "🤍 التفاهم ممكن ببعض الجهد."
    else:
        desc = "💔 التوافق ضعيف.. لكن لا شيء مستحيل!"

    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='md',
            contents=[
                TextComponent(text="🔮 توافق الأسماء", weight='bold', size='lg', color=COLOR_PRIMARY),
                TextComponent(text=f"{name1} 💞 {name2}", size='md', weight='bold', color=COLOR_SECONDARY),
                TextComponent(text=f"نسبة التوافق: {percentage}%", size='sm', color=COLOR_PRIMARY),
                TextComponent(text=desc, size='sm', color=COLOR_SECONDARY)
            ],
            background_color=COLOR_BG,
            padding_all="12px",
            corner_radius="10px"
        )
    )
    return FlexSendMessage(alt_text="توافق الأسماء", contents=bubble)
