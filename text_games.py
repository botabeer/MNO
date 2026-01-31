# text_games.py - الالعاب النصية بدون تسجيل

import random
import os

def read_lines_from_file(filename):
    """قراءة الاسطر من ملف"""
    filepath = os.path.join('games', filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines
    except FileNotFoundError:
        return []

def get_random_question():
    """الحصول على سؤال عشوائي"""
    questions = read_lines_from_file('questions.txt')
    if not questions:
        return "لا توجد اسئلة متاحة حاليا"
    return random.choice(questions)

def get_random_challenge():
    """الحصول على تحدي عشوائي"""
    challenges = read_lines_from_file('challenges.txt')
    if not challenges:
        return "لا توجد تحديات متاحة حاليا"
    return random.choice(challenges)

def get_random_confession():
    """الحصول على اعتراف عشوائي"""
    confessions = read_lines_from_file('confessions.txt')
    if not confessions:
        return "لا توجد اعترافات متاحة حاليا"
    return random.choice(confessions)

def get_random_mention():
    """الحصول على منشن عشوائي"""
    mentions = read_lines_from_file('mentions.txt')
    if not mentions:
        return "لا توجد منشنات متاحة حاليا"
    return random.choice(mentions)
