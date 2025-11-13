from linebot.models import QuickReply, QuickReplyButton, MessageAction

def get_quick_reply():
    """الأزرار السريعة الرئيسية - الألعاب"""
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="▫️أسرع", text="أسرع")),
        QuickReplyButton(action=MessageAction(label="▫️ذكاء", text="ذكاء")),
        QuickReplyButton(action=MessageAction(label="▫️لون", text="كلمة ولون")),
        QuickReplyButton(action=MessageAction(label="▫️أغنية", text="أغنية")),
        QuickReplyButton(action=MessageAction(label="▫️سلسلة", text="سلسلة")),
        QuickReplyButton(action=MessageAction(label="▫️ترتيب", text="ترتيب الحروف")),
        QuickReplyButton(action=MessageAction(label="▫️تكوين", text="تكوين كلمات")),
        QuickReplyButton(action=MessageAction(label="▫️لعبة", text="لعبة")),
        QuickReplyButton(action=MessageAction(label="▫️خمن", text="خمن")),
        QuickReplyButton(action=MessageAction(label="▫️ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="▫️ذاكرة", text="ذاكرة")),
        QuickReplyButton(action=MessageAction(label="▫️لغز", text="لغز")),
        QuickReplyButton(action=MessageAction(label="▫️رياضيات", text="رياضيات"))
    ])

def get_more_quick_reply():
    """أزرار الألعاب الإضافية"""
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="▫️إيموجي", text="إيموجي")),
        QuickReplyButton(action=MessageAction(label="▫️توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="▫️مساعدة", text="مساعدة"))
    ])

def get_winner_announcement(winner_name, winner_points, game_type, total_questions=5):
    """نافذة إعلان الفائز - Flex Message"""
    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "🏆", "size": "5xl", "align": "center", "color": "#FFD700"},
                {"type": "text", "text": "تهانينا!", "weight": "bold", "size": "xxl", "color": "#1a1a1a", "align": "center", "margin": "md"}
            ],
            "backgroundColor": "#ffffff",
            "paddingAll": "28px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "الفائز", "size": "sm", "color": "#6a6a6a", "align": "center"},
                        {"type": "text", "text": winner_name, "weight": "bold", "size": "xl", "color": "#2a2a2a", "align": "center", "margin": "sm"}
                    ],
                    "backgroundColor": "#f5f5f5",
                    "cornerRadius": "md",
                    "paddingAll": "16px"
                },
                {"type": "separator", "margin": "xl", "color": "#e8e8e8"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "اللعبة", "size": "sm", "color": "#6a6a6a", "flex": 2},
                                {"type": "text", "text": game_type, "size": "sm", "color": "#2a2a2a", "flex": 3, "align": "end", "weight": "bold"}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "النقاط", "size": "sm", "color": "#6a6a6a", "flex": 2},
                                {"type": "text", "text": f"{winner_points} نقطة", "size": "xl", "color": "#FFD700", "flex": 3, "align": "end", "weight": "bold"}
                            ],
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "الأسئلة", "size": "sm", "color": "#6a6a6a", "flex": 2},
                                {"type": "text", "text": f"{total_questions} أسئلة", "size": "sm", "color": "#2a2a2a", "flex": 3, "align": "end", "weight": "bold"}
                            ],
                            "margin": "md"
                        }
                    ],
                    "margin": "xl"
                },
                {"type": "separator", "margin": "xl", "color": "#e8e8e8"},
                {"type": "text", "text": "🎉 أحسنت! لعبة رائعة 🎉", "size": "sm", "color": "#4a4a4a", "align": "center", "wrap": True, "margin": "xl"}
            ],
            "backgroundColor": "#ffffff",
            "paddingAll": "24px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "separator", "color": "#e8e8e8"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "button", "action": {"type": "message", "label": "▫️لعب مرة أخرى", "text": game_type}, "style": "primary", "color": "#2a2a2a", "height": "sm"},
                        {"type": "button", "action": {"type": "message", "label": "▫️الصدارة", "text": "الصدارة"}, "style": "secondary", "height": "sm"}
                    ],
                    "spacing": "sm",
                    "margin": "md"
                },
                {"type": "text", "text": "جرب لعبة أخرى من الأزرار أدناه", "size": "xs", "color": "#9a9a9a", "align": "center", "margin": "md"}
            ],
            "backgroundColor": "#f8f8f8",
            "paddingAll": "16px"
        }
    }

def get_welcome_message(display_name):
    """رسالة الترحيب الرئيسية"""
    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "منصة الألعاب", "weight": "bold", "size": "xxl", "color": "#1a1a1a", "align": "center"},
                {"type": "text", "text": f"مرحباً {display_name}", "size": "md", "color": "#6a6a6a", "align": "center", "margin": "sm"}
            ],
            "backgroundColor": "#ffffff",
            "paddingAll": "24px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "خطوات البدء", "weight": "bold", "size": "md", "color": "#2a2a2a"},
                        {"type": "separator", "margin": "md", "color": "#e8e8e8"}
                    ],
                    "spacing": "sm"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "1", "size": "sm", "color": "#ffffff", "align": "center", "weight": "bold", "flex": 0},
                                {"type": "text", "text": "اضغط على زر انضم للتسجيل", "size": "sm", "color": "#4a4a4a", "flex": 1, "margin": "md", "wrap": True}
                            ],
                            "backgroundColor": "#2a2a2a",
                            "cornerRadius": "md",
                            "paddingAll": "12px",
                            "spacing": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "2", "size": "sm", "color": "#2a2a2a", "align": "center", "weight": "bold", "flex": 0},
                                {"type": "text", "text": "اختر لعبة من الأزرار أدناه", "size": "sm", "color": "#4a4a4a", "flex": 1, "margin": "md", "wrap": True}
                            ],
                            "backgroundColor": "#f5f5f5",
                            "cornerRadius": "md",
                            "paddingAll": "12px",
                            "spacing": "md",
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "3", "size": "sm", "color": "#2a2a2a", "align": "center", "weight": "bold", "flex": 0},
                                {"type": "text", "text": "ابدأ اللعب واجمع النقاط", "size": "sm", "color": "#4a4a4a", "flex": 1, "margin": "md", "wrap": True}
                            ],
                            "backgroundColor": "#f5f5f5",
                            "cornerRadius": "md",
                            "paddingAll": "12px",
                            "spacing": "md",
                            "margin": "sm"
                        }
                    ],
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "15 لعبة متاحة", "size": "xs", "color": "#9a9a9a", "align": "center"},
                        {"type": "text", "text": "إجاباتك تُحسب تلقائياً بعد التسجيل", "size": "xs", "color": "#9a9a9a", "align": "center", "margin": "xs"}
                    ],
                    "margin": "lg"
                }
            ],
            "backgroundColor": "#ffffff",
            "paddingAll": "20px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "separator", "color": "#e8e8e8"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "button", "action": {"type": "message", "label": "▫️انضم", "text": "انضم"}, "style": "primary", "color": "#2a2a2a", "height": "sm"},
                        {"type": "button", "action": {"type": "message", "label": "▫️مساعدة", "text": "مساعدة"}, "style": "secondary", "height": "sm"}
                    ],
                    "spacing": "sm",
                    "margin": "md"
                }
            ],
            "backgroundColor": "#f8f8f8",
            "paddingAll": "16px"
        }
    }

def get_join_message(display_name):
    """رسالة التسجيل الناجح"""
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "تم التسجيل بنجاح", "weight": "bold", "size": "xl", "color": "#1a1a1a", "align": "center"},
                {"type": "text", "text": f"مرحباً بك {display_name}", "size": "md", "color": "#6a6a6a", "align": "center", "margin": "md"},
                {"type": "separator", "margin": "xl", "color": "#e8e8e8"},
                {"type": "text", "text": "يمكنك الآن اللعب في جميع الألعاب\n\nإجاباتك ستُحسب تلقائياً", "size": "sm", "color": "#4a4a4a", "align": "center", "wrap": True, "margin": "xl"}
            ],
            "backgroundColor": "#ffffff",
            "paddingAll": "28px"
        }
    }

def get_stats_message(display_name, stats, is_registered):
    """رسالة إحصائيات المستخدم"""
    status = "مسجل" if is_registered else "غير مسجل"
    status_color = "#2a2a2a" if is_registered else "#9a9a9a"
    win_rate = (stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
    
    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "إحصائياتك", "weight": "bold", "size": "xl", "color": "#1a1a1a", "align": "center"},
                {"type": "text", "text": display_name, "size": "sm", "color": "#6a6a6a", "align": "center", "margin": "sm"}
            ],
            "backgroundColor": "#ffffff",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "الحالة", "size": "sm", "color": "#6a6a6a", "flex": 2},
                        {"type": "text", "text": status, "size": "sm", "color": status_color, "flex": 3, "align": "end", "weight": "bold"}
                    ]
                },
                {"type": "separator", "margin": "md", "color": "#e8e8e8"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "النقاط", "size": "sm", "color": "#6a6a6a", "flex": 2},
                        {"type": "text", "text": str(stats['total_points']), "size": "xl", "color": "#1a1a1a", "flex": 3, "align": "end", "weight": "bold"}
                    ],
                    "margin": "md"
                },
                {"type": "separator", "margin": "md", "color": "#e8e8e8"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "الألعاب", "size": "sm", "color": "#6a6a6a", "flex": 2},
                        {"type": "text", "text": str(stats['games_played']), "size": "sm", "color": "#2a2a2a", "flex": 3, "align": "end", "weight": "bold"}
                    ],
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "الفوز", "size": "sm", "color": "#6a6a6a", "flex": 2},
                        {"type": "text", "text": str(stats['wins']), "size": "sm", "color": "#2a2a2a", "flex": 3, "align": "end", "weight": "bold"}
                    ],
                    "margin": "sm"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "نسبة الفوز", "size": "sm", "color": "#6a6a6a", "flex": 2},
                        {"type": "text", "text": f"{win_rate:.1f}%", "size": "sm", "color": "#2a2a2a", "flex": 3, "align": "end", "weight": "bold"}
                    ],
                    "margin": "sm"
                }
            ],
            "backgroundColor": "#ffffff",
            "paddingAll": "20px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "separator", "color": "#e8e8e8"},
                {"type": "button", "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"}, "style": "secondary", "height": "sm", "margin": "md"}
            ],
            "backgroundColor": "#f8f8f8",
            "paddingAll": "16px"
        }
    }

def get_leaderboard_message(leaders):
    """رسالة لوحة الصدارة"""
    players_list = []
    for i, leader in enumerate(leaders, 1):
        if i <= 3:
            rank_bg = "#4a4a4a"
            rank_color = "#ffffff"
            name_color = "#ffffff"
        else:
            rank_bg = "#f5f5f5"
            rank_color = "#2a2a2a"
            name_color = "#4a4a4a"
        
        player_box = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "text", "text": str(i), "size": "sm", "color": rank_color, "align": "center", "weight": "bold", "flex": 0},
                {"type": "text", "text": leader['display_name'], "size": "sm", "color": name_color, "flex": 3, "margin": "md", "weight": "bold" if i <= 3 else "regular"},
                {"type": "text", "text": str(leader['total_points']), "size": "sm", "color": name_color, "flex": 1, "align": "end", "weight": "bold" if i <= 3 else "regular"}
            ],
            "backgroundColor": rank_bg,
            "cornerRadius": "md",
            "paddingAll": "12px",
            "spacing": "md",
            "margin": "xs" if i > 1 else "none"
        }
        players_list.append(player_box)
    
    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "لوحة الصدارة", "weight": "bold", "size": "xl", "color": "#1a1a1a", "align": "center"},
                {"type": "text", "text": "أفضل اللاعبين", "size": "sm", "color": "#6a6a6a", "align": "center", "margin": "sm"}
            ],
            "backgroundColor": "#ffffff",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": players_list,
            "backgroundColor": "#ffffff",
            "paddingAll": "20px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "separator", "color": "#e8e8e8"},
                {"type": "button", "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"}, "style": "secondary", "height": "sm", "margin": "md"}
            ],
            "backgroundColor": "#f8f8f8",
            "paddingAll": "16px"
        }
    }

def get_help_message():
    """رسالة المساعدة"""
    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "دليل الاستخدام", "weight": "bold", "size": "xxl", "color": "#1a1a1a", "align": "center"}
            ],
            "backgroundColor": "#ffffff",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "الأوامر الأساسية", "weight": "bold", "size": "lg", "color": "#2a2a2a", "margin": "none"},
                        {"type": "separator", "margin": "md", "color": "#e8e8e8"}
                    ],
                    "margin": "none",
                    "spacing": "sm"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "انضم", "size": "sm", "color": "#1a1a1a", "flex": 2, "weight": "bold"},
                                {"type": "text", "text": "التسجيل في البوت", "size": "sm", "color": "#6a6a6a", "flex": 5, "wrap": True}
                            ],
                            "spacing": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "نقاطي", "size": "sm", "color": "#1a1a1a", "flex": 2, "weight": "bold"},
                                {"type": "text", "text": "عرض إحصائياتك", "size": "sm", "color": "#6a6a6a", "flex": 5, "wrap": True}
                            ],
                            "spacing": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "الصدارة", "size": "sm", "color": "#1a1a1a", "flex": 2, "weight": "bold"},
                                {"type": "text", "text": "أفضل اللاعبين", "size": "sm", "color": "#6a6a6a", "flex": 5, "wrap": True}
                            ],
                            "spacing": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "إيقاف", "size": "sm", "color": "#1a1a1a", "flex": 2, "weight": "bold"},
                                {"type": "text", "text": "إنهاء اللعبة الحالية", "size": "sm", "color": "#6a6a6a", "flex": 5, "wrap": True}
                            ],
                            "spacing": "md"
                        }
                    ],
                    "spacing": "md",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "أثناء اللعب", "weight": "bold", "size": "lg", "color": "#2a2a2a", "margin": "none"},
                        {"type": "separator", "margin": "md", "color": "#e8e8e8"}
                    ],
                    "margin": "xl",
                    "spacing": "sm"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "لمح", "size": "sm", "color": "#1a1a1a", "flex": 2, "weight": "bold"},
                                {"type": "text", "text": "الحصول على تلميح", "size": "sm", "color": "#6a6a6a", "flex": 5, "wrap": True}
                            ],
                            "spacing": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "جاوب", "size": "sm", "color": "#1a1a1a", "flex": 2, "weight": "bold"},
                                {"type": "text", "text": "عرض الإجابة الصحيحة", "size": "sm", "color": "#6a6a6a", "flex": 5, "wrap": True}
                            ],
                            "spacing": "md"
                        }
                    ],
                    "spacing": "md",
                    "margin": "md"
                }
            ],
            "spacing": "md",
            "backgroundColor": "#ffffff",
            "paddingAll": "20px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "separator", "color": "#e8e8e8"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "button", "action": {"type": "message", "label": "انضم", "text": "انضم"}, "style": "primary", "color": "#2a2a2a", "height": "sm"},
                        {"type": "button", "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"}, "style": "secondary", "height": "sm"},
                        {"type": "button", "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"}, "style": "secondary", "height": "sm"}
                    ],
                    "spacing": "sm",
                    "margin": "md"
                },
                {"type": "text", "text": "تم إنشاء هذا البوت بواسطة عبير الدوسري", "size": "xs", "color": "#9a9a9a", "align": "center", "wrap": True, "margin": "md"}
            ],
            "backgroundColor": "#f8f8f8",
            "paddingAll": "16px"
        }
    }
