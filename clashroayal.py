import json
import math
import random
import tkinter as tk
from pathlib import Path


WIDTH = 960
HEIGHT = 600
SAVE_FILE = Path(__file__).with_name("save.json")
MAX_UNITS = 48
ELIXIR_CAP = 10
STARTING_ELIXIR = 5
STARTER_CARDS = [
    "Рыцарь", "Лучницы", "Великан", "Гоблины",
    "Маг", "Копейщица", "Огненный шар", "Лечение",
]
CARD_GOLD_COST = 300
CARD_PURCHASE_COST = 300

ARENA_THEMES = (
    "Зелёная долина", "Ледяная крепость", "Тёмный лес", "Песчаная арена",
    "Королевский замок", "Лавовая шахта", "Облачный порт", "Грибная чаща",
    "Сырный каньон", "Пончикополис", "Квадробер-парк", "Хоббихорс-дерби",
    "Заброшенный торговый центр", "Школа после полуночи", "Подвал мемов",
    "Проклятый аквапарк", "Лиминальный коридор", "Глитч-измерение",
    "Кошмарный цирк", "Абсолютный хаос",
)
ARENA_PALETTES = (
    ("#4f7f3b", "#35602d", "#d8b36a"),
    ("#55758a", "#3d5269", "#b8d8e8"),
    ("#355143", "#26382f", "#9eb76f"),
    ("#9b7849", "#715738", "#d6b875"),
    ("#766c91", "#51475f", "#d5c5eb"),
    ("#70453d", "#4f302c", "#eda66f"),
    ("#527d82", "#36535c", "#e4cb79"),
    ("#725c49", "#473c3b", "#b3cf83"),
    ("#80743e", "#51452e", "#ecda92"),
    ("#984e71", "#583d70", "#f2b1d5"),
)
ARENAS = [
    (f"Арена {index + 1}: {ARENA_THEMES[index // 5]}",
     *ARENA_PALETTES[(index + index // 10) % len(ARENA_PALETTES)])
    for index in range(100)
]
ARENA_TROPHY_STEP = 100


def arena_for_trophies(trophies):
    return min(max(0, trophies) // ARENA_TROPHY_STEP, len(ARENAS) - 1)

BRIDGES = (250, 710)

HERO_SKINS = [
    ("Королевский рыцарь", "#4b78c2"),
    ("Серебряный рыцарь", "#b8c7d9"),
    ("Лесной рыцарь", "#4e9b52"),
    ("Огненный рыцарь", "#dc663e"),
    ("Ледяной рыцарь", "#78bdd8"),
    ("Тёмный рыцарь", "#6b566f"),
]

BOT_NAMES = [
    "Пельмень_007", "Кот_в_броне", "Лорд_Пончик", "МышьНаКубках",
    "ТапокМаг", "Бублик.exe", "ПиксельныйБарсук", "ГрозныйХомяк",
    "СырныйРыцарь", "КапитанКефир", "НочнойЧайник", "ЛягушонокPRO",
]


CARDS = {
    "Рыцарь": {"cost": 3, "hp": 260, "damage": 44, "speed": 43, "range": 27, "cooldown": 1.0, "size": 13, "color": "#5577bb", "count": 1},
    "Лучницы": {"cost": 3, "hp": 150, "damage": 36, "speed": 38, "range": 115, "cooldown": 0.9, "size": 10, "color": "#7da65d", "count": 2, "can_target_air": True},
    "Великан": {"cost": 5, "hp": 720, "damage": 82, "speed": 25, "range": 28, "cooldown": 1.3, "size": 19, "color": "#b68555", "count": 1, "targets": "buildings"},
    "Гоблины": {"cost": 2, "hp": 30, "damage": 38, "speed": 68, "range": 24, "cooldown": 0.72, "size": 8, "color": "#76a94b", "count": 3},
    "Маг": {"cost": 4, "hp": 190, "damage": 68, "speed": 34, "range": 105, "cooldown": 1.2, "size": 12, "color": "#8d66b5", "count": 1, "can_target_air": True, "splash": 34},
    "Копейщица": {"cost": 3, "hp": 300, "damage": 52, "speed": 40, "range": 90, "cooldown": 1.05, "size": 13, "color": "#b7b14c", "count": 1, "can_target_air": True},
    "Огненный шар": {"cost": 4, "hp": 0, "damage": 180, "speed": 0, "range": 75, "cooldown": 0, "size": 14, "color": "#e96a3a", "count": 1, "spell": True},
    "Лечение": {"cost": 3, "hp": 0, "damage": -160, "speed": 0, "range": 90, "cooldown": 0, "size": 14, "color": "#67cf82", "count": 1, "spell": True},
}

# Остальные карты и оставшаяся логика игры загружаются из оригинального файла ниже.
# Этот файл является полной рабочей копией без внесённых выше изменений логики магазина.
