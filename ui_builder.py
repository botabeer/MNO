class UIBuilder:
    COLORS = {
        'primary': '#2563EB',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'text': '#1F2937',
        'text_light': '#6B7280',
        'border': '#E5E7EB',
        'bg': '#F9FAFB'
    }
    
    def welcome_card(self, display_name, is_registered):
        status = "مسجل" if is_registered else "غير مسجل"
        status_color = self.COLORS['success'] if is_registered else self.COLORS['warning']
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    self._header("بوت الحوت"),
                    self._text_box(f"مرحبا {display_name}", "lg", "center"),
                    self._text_box(status, "sm", "center", status_color),
                    self._separator(),
                    self._button_row([
                        ("العاب", "العاب"),
                        ("نقاطي", "نقاطي")
                    ]),
                    self._button_row([
                        ("الصدارة", "الصدارة"),
                        ("مساعدة", "مساعدة")
                    ]),
                    self._separator(),
                    self._text_box("للتسجيل او تغيير الاسم اكتب: تسجيل", "xs", "center", self.COLORS['text_light'])
                ],
                "paddingAll": "20px"
            }
        }
    
    def games_menu_card(self):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    self._header("قائمة الالعاب"),
                    self._text_box("العاب تنافسية", "md", "center", self.COLORS['primary']),
                    self._button_row([
                        ("اغنيه", "اغنيه"),
                        ("ضد", "ضد"),
                        ("سلسلة", "سلسله")
                    ]),
                    self._button_row([
                        ("اسرع", "اسرع"),
                        ("تكوين", "تكوين"),
                        ("فئة", "فئه")
                    ]),
                    self._separator(),
                    self._text_box("العاب ترفيهية", "md", "center", self.COLORS['success']),
                    self._button_row([
                        ("لعبة", "لعبه"),
                        ("توافق", "توافق")
                    ])
                ],
                "paddingAll": "20px"
            }
        }
    
    def help_card(self):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    self._header("دليل الاستخدام"),
                    self._info_section("الاوامر الاساسية", "بداية - العاب - نقاطي - الصدارة - تسجيل"),
                    self._separator(),
                    self._info_section("الالعاب التنافسية", "اغنيه - ضد - سلسلة - اسرع - تكوين - فئة"),
                    self._separator(),
                    self._info_section("العاب ترفيهية", "لعبة - توافق"),
                    self._separator(),
                    self._info_section("اثناء اللعب", "لمح - جاوب - ايقاف"),
                    self._separator(),
                    self._info_section("النقاط", "كل اجابة صحيحة = 1 نقطة")
                ],
                "paddingAll": "20px"
            }
        }
    
    def stats_card(self, display_name, stats):
        if not stats:
            stats = {'total_points': 0, 'games_played': 0, 'wins': 0}
        
        win_rate = round((stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0)
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    self._header("احصائياتك"),
                    self._text_box(display_name, "xl", "center", self.COLORS['primary']),
                    self._separator(),
                    self._stat_row("النقاط", str(stats['total_points'])),
                    self._stat_row("الالعاب", str(stats['games_played'])),
                    self._stat_row("الفوز", str(stats['wins'])),
                    self._stat_row("نسبة الفوز", f"{win_rate}%")
                ],
                "paddingAll": "20px"
            }
        }
    
    def leaderboard_card(self, leaders):
        leader_list = []
        
        for i, leader in enumerate(leaders[:20], 1):
            leader_list.append(self._leader_row(
                str(i),
                leader['display_name'],
                str(leader['total_points'])
            ))
        
        if not leader_list:
            leader_list.append(self._text_box("لا توجد بيانات", "sm", "center", self.COLORS['text_light']))
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    self._header("لوحة الصدارة"),
                    *leader_list
                ],
                "paddingAll": "20px"
            }
        }
    
    def _header(self, text):
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [{
                "type": "text",
                "text": text,
                "weight": "bold",
                "size": "xl",
                "color": "#FFFFFF",
                "align": "center"
            }],
            "backgroundColor": self.COLORS['primary'],
            "paddingAll": "15px",
            "cornerRadius": "10px",
            "margin": "none"
        }
    
    def _text_box(self, text, size="md", align="start", color=None):
        return {
            "type": "text",
            "text": text,
            "size": size,
            "align": align,
            "color": color or self.COLORS['text'],
            "wrap": True,
            "margin": "md"
        }
    
    def _separator(self):
        return {
            "type": "separator",
            "margin": "md",
            "color": self.COLORS['border']
        }
    
    def _button_row(self, buttons):
        button_elements = []
        for label, action_text in buttons:
            button_elements.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": label,
                    "text": action_text
                },
                "style": "secondary",
                "height": "sm",
                "flex": 1
            })
        
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": button_elements,
            "spacing": "sm",
            "margin": "md"
        }
    
    def _info_section(self, title, content):
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": title,
                    "weight": "bold",
                    "size": "sm",
                    "color": self.COLORS['primary']
                },
                {
                    "type": "text",
                    "text": content,
                    "size": "xs",
                    "color": self.COLORS['text_light'],
                    "wrap": True,
                    "margin": "xs"
                }
            ],
            "margin": "md"
        }
    
    def _stat_row(self, label, value):
        return {
            "type": "box",
            "layout": "baseline",
            "contents": [
                {
                    "type": "text",
                    "text": label,
                    "size": "sm",
                    "color": self.COLORS['text_light'],
                    "flex": 3
                },
                {
                    "type": "text",
                    "text": value,
                    "size": "lg",
                    "weight": "bold",
                    "color": self.COLORS['primary'],
                    "align": "end",
                    "flex": 2
                }
            ],
            "margin": "md"
        }
    
    def _leader_row(self, rank, name, points):
        return {
            "type": "box",
            "layout": "baseline",
            "contents": [
                {
                    "type": "text",
                    "text": rank,
                    "size": "sm",
                    "color": self.COLORS['text_light'],
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": name,
                    "size": "sm",
                    "color": self.COLORS['text'],
                    "flex": 3,
                    "margin": "sm"
                },
                {
                    "type": "text",
                    "text": points,
                    "size": "sm",
                    "weight": "bold",
                    "color": self.COLORS['primary'],
                    "align": "end",
                    "flex": 1
                }
            ],
            "margin": "sm"
        }
