"""
مكونات واجهة المستخدم - Flex Messages
"""

def get_simple_card(title, content, buttons=None):
    """بطاقة بسيطة"""
    card = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": title,
                    "size": "xl",
                    "weight": "bold",
                    "color": "#000000",
                    "align": "center"
                },
                {
                    "type": "separator",
                    "margin": "xl",
                    "color": "#CCCCCC"
                },
                {
                    "type": "text",
                    "text": content,
                    "size": "md",
                    "color": "#333333",
                    "wrap": True,
                    "margin": "xl",
                    "align": "center"
                }
            ],
            "backgroundColor": "#FFFFFF",
            "paddingAll": "24px"
        }
    }
    
    if buttons:
        card["footer"] = {
            "type": "box",
            "layout": "horizontal",
            "contents": buttons,
            "spacing": "sm",
            "backgroundColor": "#F5F5F5",
            "paddingAll": "16px"
        }
    
    return card

def get_progress_bar(current, total, label="التقدم"):
    """شريط التقدم"""
    percentage = (current / total) * 100
    
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": f"{label}: {current}/{total}",
                "size": "sm",
                "color": "#666666"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "width": f"{percentage}%",
                        "backgroundColor": "#000000",
                        "height": "6px"
                    }
                ],
                "backgroundColor": "#E5E5E5",
                "height": "6px",
                "margin": "sm"
            }
        ]
    }

def get_score_badge(score, label="النقاط"):
    """شارة النقاط"""
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": str(score),
                "size": "xxl",
                "weight": "bold",
                "color": "#000000",
                "align": "center"
            },
            {
                "type": "text",
                "text": label,
                "size": "xs",
                "color": "#666666",
                "align": "center",
                "margin": "xs"
            }
        ],
        "backgroundColor": "#F5F5F5",
        "cornerRadius": "10px",
        "paddingAll": "16px"
    }
```

---

## 📋 **ملخص الهيكل النهائي:**
```
bot/
├── app.py (الملف الرئيسي المحدث)
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env.example
├── .gitignore
├── game_scores.db (يُنشأ تلقائياً)
│
├── games/
│   ├── __init__.py
│   ├── song_game.py ✅
│   ├── opposite_game.py ✅
│   ├── compatibility_game.py ✅
│   ├── differences_game.py ✅
│   ├── fast_typing_game.py ✅
│   ├── chain_words_game.py ✅
│   ├── human_animal_plant_game.py ✅
│   ├── letters_words_game.py ✅
│   ├── questions.txt
│   ├── challenges.txt
│   ├── confessions.txt
│   └── more_questions.txt
│
└── utils/
    ├── __init__.py
    ├── helpers.py
    ├── database.py
    └── ui_components.py
