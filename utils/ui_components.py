"""
UI Components Module - مكونات واجهة المستخدم
===========================================
تصميم أنيق ومريح للعين بألوان احترافية
"""

from linebot.models import (
    FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, SeparatorComponent, FillerComponent,
    QuickReply, QuickReplyButton, MessageAction
)
from typing import List, Dict
from .helpers import format_number, calculate_win_rate, get_level_info

# ألوان التصميم الاحترافي
COLORS = {
    'primary': '#000000',      # أسود
    'secondary': '#6B7280',    # رمادي متوسط
    'light_gray': '#D1D5DB',   # رمادي فاتح
    'background': '#FFFFFF',   # أبيض
    'accent': '#9CA3AF',       # رمادي ناعم
    'success': '#10B981',      # أخضر ناعم
    'warning': '#F59E0B',      # برتقالي ناعم
    'danger': '#EF4444'        # أحمر ناعم
}

def create_flex_message(
    title: str,
    body: str,
    color: str = COLORS['primary'],
    add_quick_reply: bool = True
) -> FlexSendMessage:
    """
    إنشاء رسالة Flex بتصميم أنيق
    
    Args:
        title: العنوان
        body: المحتوى
        color: لون العنوان
        add_quick_reply: إضافة الأزرار السريعة
    """
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='md',
            padding_all='16px',
            background_color=COLORS['background'],
            contents=[
                # العنوان
                TextComponent(
                    text=title,
                    weight='bold',
                    size='xl',
                    color=color,
                    wrap=True,
                    align='start'
                ),
                # خط فاصل رفيع
                SeparatorComponent(
                    margin='md',
                    color=COLORS['light_gray']
                ),
                # المحتوى
                TextComponent(
                    text=body,
                    size='md',
                    color=COLORS['secondary'],
                    wrap=True,
                    margin='md',
                    align='start',
                    line_spacing='lg'
                )
            ]
        ),
        styles={
            'body': {
                'separator': True,
                'backgroundColor': COLORS['background']
            }
        }
    )
    
    quick_reply = get_quick_reply_buttons() if add_quick_reply else None
    
    return FlexSendMessage(
        alt_text=title,
        contents=bubble,
        quick_reply=quick_reply
    )

def create_welcome_bubble(display_name: str) -> FlexSendMessage:
    """
    رسالة الترحيب الأنيقة
    """
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='md',
            padding_all='20px',
            background_color=COLORS['background'],
            contents=[
                # أيقونة الترحيب
                TextComponent(
                    text='👋',
                    size='5xl',
                    align='center',
                    margin='none'
                ),
                # الترحيب
                TextComponent(
                    text=f'مرحباً {display_name}',
                    weight='bold',
                    size='xxl',
                    color=COLORS['primary'],
                    align='center',
                    margin='md'
                ),
                # خط فاصل
                SeparatorComponent(
                    margin='lg',
                    color=COLORS['light_gray']
                ),
                # الوصف
                TextComponent(
                    text='اختر اللعبة التي تريد لعبها من الأزرار أدناه',
                    size='md',
                    color=COLORS['secondary'],
                    align='center',
                    wrap=True,
                    margin='lg'
                ),
                # نصيحة
                BoxComponent(
                    layout='vertical',
                    margin='xl',
                    padding_all='12px',
                    background_color='#F9FAFB',
                    corner_radius='8px',
                    contents=[
                        TextComponent(
                            text='💡 نصيحة',
                            size='sm',
                            color=COLORS['accent'],
                            weight='bold'
                        ),
                        TextComponent(
                            text='اكتب "مساعدة" لعرض جميع الأوامر',
                            size='xs',
                            color=COLORS['secondary'],
                            margin='xs'
                        )
                    ]
                )
            ]
        )
    )
    
    return FlexSendMessage(
        alt_text='مرحباً بك',
        contents=bubble,
        quick_reply=get_quick_reply_buttons()
    )

def create_stats_bubble(user_stats: Dict) -> FlexSendMessage:
    """
    عرض إحصائيات اللاعب بتصميم جميل
    """
    level_info = get_level_info(user_stats['total_points'])
    win_rate = calculate_win_rate(user_stats['wins'], user_stats['games_played'])
    
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='md',
            padding_all='20px',
            background_color=COLORS['background'],
            contents=[
                # رأس البطاقة
                BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(
                            text='📊',
                            size='3xl',
                            flex=0
                        ),
                        BoxComponent(
                            layout='vertical',
                            margin='md',
                            contents=[
                                TextComponent(
                                    text=user_stats['display_name'],
                                    weight='bold',
                                    size='xl',
                                    color=COLORS['primary']
                                ),
                                TextComponent(
                                    text=f"{level_info['emoji']} {level_info['title']}",
                                    size='sm',
                                    color=COLORS['accent'],
                                    margin='xs'
                                )
                            ]
                        )
                    ]
                ),
                SeparatorComponent(margin='lg', color=COLORS['light_gray']),
                
                # الإحصائيات الرئيسية
                BoxComponent(
                    layout='vertical',
                    margin='lg',
                    spacing='md',
                    contents=[
                        _create_stat_row('النقاط', format_number(user_stats['total_points']), '⭐'),
                        _create_stat_row('الألعاب', str(user_stats['games_played']), '🎮'),
                        _create_stat_row('الفوز', str(user_stats['wins']), '🏆'),
                        _create_stat_row('نسبة الفوز', f"{win_rate}%", '📈'),
                        _create_stat_row('أفضل سلسلة', str(user_stats.get('best_streak', 0)), '🔥')
                    ]
                ),
                
                # شريط التقدم للمستوى التالي
                BoxComponent(
                    layout='vertical',
                    margin='xl',
                    padding_all='12px',
                    background_color='#F9FAFB',
                    corner_radius='8px',
                    contents=[
                        TextComponent(
                            text=f"المستوى التالي: {level_info.get('points_needed', 0)} نقطة",
                            size='xs',
                            color=COLORS['secondary'],
                            align='center'
                        )
                    ]
                ) if level_info.get('points_needed', 0) > 0 else FillerComponent()
            ]
        )
    )
    
    return FlexSendMessage(
        alt_text='إحصائياتك',
        contents=bubble,
        quick_reply=get_quick_reply_buttons()
    )

def _create_stat_row(label: str, value: str, emoji: str) -> BoxComponent:
    """
    صف إحصائية واحد
    """
    return BoxComponent(
        layout='horizontal',
        contents=[
            TextComponent(
                text=f"{emoji} {label}",
                size='sm',
                color=COLORS['secondary'],
                flex=3
            ),
            TextComponent(
                text=value,
                size='sm',
                color=COLORS['primary'],
                weight='bold',
                flex=2,
                align='end'
            )
        ]
    )

def create_leaderboard_bubble(leaders: List[Dict]) -> FlexSendMessage:
    """
    لوحة الصدارة بتصميم أنيق
    """
    medal_emojis = ['🥇', '🥈', '🥉']
    
    leader_contents = []
    
    for i, leader in enumerate(leaders):
        medal = medal_emojis[i] if i < 3 else f"{i+1}."
        
        leader_box = BoxComponent(
            layout='horizontal',
            margin='md',
            padding_all='12px',
            background_color='#F9FAFB' if i % 2 == 0 else COLORS['background'],
            corner_radius='8px',
            contents=[
                # الترتيب
                TextComponent(
                    text=medal,
                    size='lg',
                    flex=0,
                    margin='none'
                ),
                # الاسم
                BoxComponent(
                    layout='vertical',
                    margin='md',
                    flex=4,
                    contents=[
                        TextComponent(
                            text=leader['display_name'],
                            size='md',
                            color=COLORS['primary'],
                            weight='bold'
                        ),
                        TextComponent(
                            text=f"{leader['wins']} فوز من {leader['games_played']} لعبة",
                            size='xs',
                            color=COLORS['accent'],
                            margin='xs'
                        )
                    ]
                ),
                # النقاط
                TextComponent(
                    text=format_number(leader['total_points']),
                    size='md',
                    color=COLORS['success'],
                    weight='bold',
                    flex=2,
                    align='end'
                )
            ]
        )
        
        leader_contents.append(leader_box)
    
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='none',
            padding_all='20px',
            background_color=COLORS['background'],
            contents=[
                # العنوان
                BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(
                            text='🏆',
                            size='3xl',
                            flex=0
                        ),
                        TextComponent(
                            text='لوحة الصدارة',
                            weight='bold',
                            size='xxl',
                            color=COLORS['primary'],
                            margin='md'
                        )
                    ]
                ),
                SeparatorComponent(margin='lg', color=COLORS['light_gray']),
                
                # قائمة المتصدرين
                BoxComponent(
                    layout='vertical',
                    margin='lg',
                    spacing='sm',
                    contents=leader_contents
                )
            ]
        )
    )
    
    return FlexSendMessage(
        alt_text='لوحة الصدارة',
        contents=bubble,
        quick_reply=get_quick_reply_buttons()
    )

def create_game_result_bubble(
    game_name: str,
    winner_name: str,
    points: int,
    is_victory: bool = True
) -> FlexSendMessage:
    """
    نتيجة اللعبة بتصميم جذاب
    """
    emoji = '🎉' if is_victory else '😔'
    title = 'فوز!' if is_victory else 'خسارة'
    color = COLORS['success'] if is_victory else COLORS['danger']
    
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='md',
            padding_all='20px',
            background_color=COLORS['background'],
            contents=[
                # الأيقونة
                TextComponent(
                    text=emoji,
                    size='5xl',
                    align='center'
                ),
                # العنوان
                TextComponent(
                    text=title,
                    weight='bold',
                    size='xxl',
                    color=color,
                    align='center',
                    margin='md'
                ),
                SeparatorComponent(margin='lg', color=COLORS['light_gray']),
                
                # التفاصيل
                BoxComponent(
                    layout='vertical',
                    margin='lg',
                    spacing='md',
                    contents=[
                        TextComponent(
                            text=f'اللعبة: {game_name}',
                            size='md',
                            color=COLORS['secondary'],
                            align='center'
                        ),
                        TextComponent(
                            text=f'الفائز: {winner_name}',
                            size='lg',
                            color=COLORS['primary'],
                            weight='bold',
                            align='center',
                            margin='sm'
                        ),
                        BoxComponent(
                            layout='horizontal',
                            margin='lg',
                            padding_all='12px',
                            background_color='#F9FAFB',
                            corner_radius='8px',
                            contents=[
                                TextComponent(
                                    text='النقاط المكتسبة',
                                    size='sm',
                                    color=COLORS['secondary'],
                                    flex=3
                                ),
                                TextComponent(
                                    text=f'+{points}',
                                    size='xl',
                                    color=COLORS['success'],
                                    weight='bold',
                                    flex=2,
                                    align='end'
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    )
    
    return FlexSendMessage(
        alt_text=f'{title} - {game_name}',
        contents=bubble,
        quick_reply=get_quick_reply_buttons()
    )

def get_quick_reply_buttons() -> QuickReply:
    """
    الأزرار السريعة الثابتة بتصميم محسّن
    """
    buttons = [
        ('🎵 أغنية', 'أغنية'),
        ('🎮 لعبة', 'لعبة'),
        ('⛓️ سلسلة', 'سلسلة'),
        ('⚡ أسرع', 'أسرع'),
        ('🔄 ضد', 'ضد'),
        ('🔤 كوّن', 'كوّن'),
        ('🔍 اختلاف', 'اختلاف'),
        ('💖 توافق', 'توافق'),
        ('❓ سؤال', 'سؤال'),
        ('🎯 تحدي', 'تحدي'),
        ('🤫 اعتراف', 'اعتراف'),
        ('➕ اكثر', 'اكثر')
    ]
    
    items = [
        QuickReplyButton(
            action=MessageAction(label=label, text=text)
        ) for label, text in buttons
    ]
    
    return QuickReply(items=items)

def create_help_bubble() -> FlexSendMessage:
    """
    رسالة المساعدة بتصميم منظم
    """
    commands = [
        ('🎮 الألعاب', 'استخدم الأزرار لبدء أي لعبة'),
        ('📊 نقاطي', 'عرض إحصائياتك الشخصية'),
        ('🏆 الصدارة', 'مشاهدة قائمة المتصدرين'),
        ('✅ انضم', 'التسجيل للمشاركة في الألعاب'),
        ('🚪 انسحب', 'الخروج من اللعبة الحالية'),
        ('⏸️ إيقاف', 'إيقاف اللعبة الجارية')
    ]
    
    command_contents = [
        BoxComponent(
            layout='horizontal',
            margin='md',
            contents=[
                TextComponent(
                    text=cmd,
                    size='md',
                    color=COLORS['primary'],
                    weight='bold',
                    flex=2
                ),
                TextComponent(
                    text=desc,
                    size='sm',
                    color=COLORS['secondary'],
                    wrap=True,
                    flex=5
                )
            ]
        ) for cmd, desc in commands
    ]
    
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='md',
            padding_all='20px',
            background_color=COLORS['background'],
            contents=[
                TextComponent(
                    text='📜 قائمة الأوامر',
                    weight='bold',
                    size='xxl',
                    color=COLORS['primary']
                ),
                SeparatorComponent(margin='lg', color=COLORS['light_gray']),
                BoxComponent(
                    layout='vertical',
                    margin='lg',
                    spacing='sm',
                    contents=command_contents
                )
            ]
        )
    )
    
    return FlexSendMessage(
        alt_text='قائمة الأوامر',
        contents=bubble,
        quick_reply=get_quick_reply_buttons()
    )
