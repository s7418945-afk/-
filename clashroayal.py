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

CARD_UNLOCK_COSTS = {
    "Обычная": 100,
    "Редкая": 250,
    "Эпичная": 500,
    "Сверхредкая": 900,
    "Легендарная": 1500,
    "Супергеройская": 2500,
}

CARD_UPGRADE_COSTS = {
    "Обычная": 40,
    "Редкая": 75,
    "Эпичная": 130,
    "Сверхредкая": 220,
    "Легендарная": 360,
    "Супергеройская": 550,
}


def card_unlock_cost(card):
    return CARD_UNLOCK_COSTS.get(CARDS[card]["rarity"], CARD_GOLD_COST)


def card_upgrade_cost(card, level):
    rarity = CARDS[card]["rarity"]
    base_cost = CARD_UPGRADE_COSTS.get(rarity, CARD_GOLD_COST)
    return base_cost * level


def battle_gold_reward(trophies, won):
    trophies = max(0, trophies)
    if trophies < 100:
        win_reward = 25 + round(trophies * 0.25)
    elif trophies < 500:
        win_reward = 50 + round((trophies - 100) * 0.25)
    else:
        win_reward = 150 + min(350, round((trophies - 500) * 0.125))
    if won:
        return min(500, win_reward)
    return max(10, round(win_reward * 0.4))


def battle_player_won(player_crowns, bot_crowns, player_elixir, bot_elixir,
                      forced_winner=None):
    if player_crowns >= 3 and bot_crowns < 3:
        return True
    if bot_crowns >= 3 and player_crowns < 3:
        return False
    if forced_winner is not None:
        return forced_winner == "player"
    if player_crowns != bot_crowns:
        return player_crowns > bot_crowns
    return player_elixir >= bot_elixir


def overtime_timer_text(seconds):
    if seconds <= 0:
        return "РЕШАЮЩИЙ МОМЕНТ"
    minutes, remaining_seconds = divmod(math.ceil(seconds), 60)
    return f"ОВЕРТАЙМ  {minutes}:{remaining_seconds:02d}"


def overtime_tower_winner(destroyed_sides, player_hp, bot_hp):
    if destroyed_sides == {"bot"}:
        return "player"
    if destroyed_sides == {"player"}:
        return "bot"
    if player_hp > bot_hp:
        return "player"
    if bot_hp > player_hp:
        return "bot"
    return None


def balanced_bot_deck(available_cards, player_deck, deck_size=8):
    deck_size = min(deck_size, len(available_cards))
    if deck_size == 0:
        return []
    target_cost = sum(CARDS[card]["cost"] for card in player_deck) / max(1, len(player_deck))
    best_deck = random.sample(available_cards, deck_size)
    best_difference = abs(
        sum(CARDS[card]["cost"] for card in best_deck) / deck_size - target_cost
    )
    for _ in range(127):
        candidate = random.sample(available_cards, deck_size)
        average_cost = sum(CARDS[card]["cost"] for card in candidate) / deck_size
        difference = abs(average_cost - target_cost)
        if difference < best_difference:
            best_deck = candidate
            best_difference = difference
            if difference <= 0.125:
                break
    return best_deck


def accrue_battle_elixir(player_elixir, bot_elixir, gain):
    player_elixir = min(ELIXIR_CAP, player_elixir + gain)
    bot_elixir = min(ELIXIR_CAP, bot_elixir + gain, player_elixir)
    return player_elixir, bot_elixir


def tower_health_bar_y(tower):
    size = 28 if tower.crown else 21
    return tower.y+size+8 if tower.side == "bot" else tower.y-size-20


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
    "Фурри-фейерверк": {"cost": 4, "hp": 0, "damage": 172, "speed": 0, "range": 80, "cooldown": 0, "size": 14, "color": "#dc77b0", "count": 1, "spell": True, "spell_kind": "furry_fireball"},
    "Хоббихорсерский таран": {"cost": 4, "hp": 0, "damage": 172, "speed": 0, "range": 80, "cooldown": 0, "size": 16, "color": "#b69a63", "count": 1, "spell": True, "spell_kind": "horse_fireball"},
    "Копытный гул": {"cost": 3, "hp": 0, "damage": 180, "speed": 0, "range": 95, "cooldown": 0, "size": 14, "color": "#a99a67", "count": 1, "spell": True, "spell_kind": "horse_stun"},
    "Мур-регенерация": {"cost": 3, "hp": 0, "damage": -180, "speed": 0, "range": 95, "cooldown": 0, "size": 14, "color": "#77cf9b", "count": 1, "spell": True, "spell_kind": "furry_heal"},
    "Лечение": {"cost": 3, "hp": 0, "damage": -160, "speed": 0, "range": 90, "cooldown": 0, "size": 14, "color": "#67cf82", "count": 1, "spell": True},
    "Страж": {"cost": 4, "hp": 390, "damage": 54, "speed": 31, "range": 30, "cooldown": 1.0, "size": 15, "color": "#8f7357", "count": 1},
    "Летучие мыши": {"cost": 2, "hp": 30, "damage": 30, "speed": 76, "range": 25, "cooldown": 0.7, "size": 8, "color": "#715c92", "count": 3, "flying": True, "can_target_air": True},
    "Тролль": {"cost": 5, "hp": 650, "damage": 76, "speed": 27, "range": 32, "cooldown": 1.35, "size": 18, "color": "#7f9b52", "count": 1, "targets": "buildings"},
    "Молния": {"cost": 4, "hp": 0, "damage": 145, "speed": 0, "range": 90, "cooldown": 0, "size": 14, "color": "#87c9ed", "count": 1, "spell": True},
    "Арбалетчик": {"cost": 3, "hp": 175, "damage": 52, "speed": 33, "range": 150, "cooldown": 1.15, "size": 11, "color": "#8774b2", "count": 1, "can_target_air": True},
    "Голем": {"cost": 6, "hp": 1050, "damage": 110, "speed": 18, "range": 30, "cooldown": 1.65, "size": 22, "color": "#8c806c", "count": 1, "targets": "buildings"},
    "Дракончик": {"cost": 4, "hp": 300, "damage": 56, "speed": 43, "range": 105, "cooldown": 1.1, "size": 14, "color": "#bd694d", "count": 1, "flying": True, "can_target_air": True},
    "Ледяной маг": {"cost": 4, "hp": 210, "damage": 42, "speed": 35, "range": 100, "cooldown": 1.15, "size": 12, "color": "#79b9d1", "count": 1, "can_target_air": True, "ice_aura": True, "slow_duration": 1.8},
    "Электро": {"cost": 4, "hp": 240, "damage": 48, "speed": 36, "range": 95, "cooldown": 1.25, "size": 13, "color": "#5cafe0", "count": 1, "can_target_air": True, "spawn_lightning": True},
    "Клетка с гоблином": {
        "cost": 4, "hp": 620, "damage": 0, "speed": 0, "range": 0,
        "cooldown": 1, "size": 18, "color": "#89734d", "count": 1,
        "building": True, "lifetime": 30, "targets": "buildings",
        "death_spawn": {
            "hp": 220, "damage": 58, "speed": 59, "range": 26,
            "cooldown": 0.85, "size": 11, "color": "#82af4c",
            "count": 1,
        },
    },
    "Манящая пушка": {
        "cost": 4, "hp": 560, "damage": 48, "speed": 0, "range": 155,
        "cooldown": 0.9, "size": 17, "color": "#9d7657", "count": 1,
        "building": True, "lifetime": 25, "taunt": True,
        "can_target_air": True,
    },
    "Небесный бомбардир": {
        "cost": 5, "hp": 290, "damage": 105, "speed": 34, "range": 115,
        "cooldown": 1.5, "size": 14, "color": "#c78150", "count": 1,
        "flying": True, "targets": "buildings", "splash": 40,
    },
    "Крылатый дракон": {
        "cost": 4, "hp": 320, "damage": 56, "speed": 43, "range": 95,
        "cooldown": 1.05, "size": 14, "color": "#55a8a4", "count": 1,
        "flying": True, "can_target_air": True, "splash": 30,
    },
    "Рой костяков": {
        "cost": 3, "hp": 30, "damage": 29, "speed": 72, "range": 23,
        "cooldown": 0.7, "size": 8, "color": "#d2d0b6", "count": 6,
    },
    "Всадник на ящере": {
        "cost": 4, "hp": 410, "damage": 84, "speed": 58, "range": 28,
        "cooldown": 1.0, "size": 15, "color": "#ad6e4c", "count": 1,
        "targets": "buildings",
    },
    "Броневой прыгун": {
        "cost": 5, "hp": 560, "damage": 76, "speed": 36, "range": 28,
        "cooldown": 1.2, "size": 18, "color": "#647e9c", "count": 1,
        "splash": 58,
    },
    "Сторожевая башня": {
        "cost": 3, "hp": 430, "damage": 38, "speed": 0, "range": 145,
        "cooldown": 0.95, "size": 16, "color": "#a78c62", "count": 1,
        "building": True, "lifetime": 22, "can_target_air": True,
    },
    "Бочка с гоблинами": {
        "cost": 3, "hp": 0, "damage": 0, "speed": 0, "range": 45,
        "cooldown": 0, "size": 14, "color": "#9b663d", "count": 1,
        "spell": True, "spell_kind": "barrel",
    },
    "Снежный волк": {
        "cost": 3, "hp": 210, "damage": 48, "speed": 62, "range": 28,
        "cooldown": 0.9, "size": 12, "color": "#d2e0e6", "count": 2,
    },
    "Лесной шаман": {
        "cost": 4, "hp": 225, "damage": 58, "speed": 35, "range": 110,
        "cooldown": 1.2, "size": 12, "color": "#73a873", "count": 1,
        "can_target_air": True,
    },
    "Гном-подрывник": {
        "cost": 3, "hp": 250, "damage": 82, "speed": 32, "range": 26,
        "cooldown": 1.3, "size": 11, "color": "#c77e48", "count": 1,
        "splash": 44,
    },
    "Ястреб-лучник": {
        "cost": 4, "hp": 185, "damage": 40, "speed": 54, "range": 135,
        "cooldown": 1.0, "size": 11, "color": "#8ba257", "count": 1,
        "flying": True, "can_target_air": True,
    },
    "Таран варваров": {
        "cost": 4, "hp": 520, "damage": 76, "speed": 65, "range": 29,
        "cooldown": 1.1, "size": 17, "color": "#9a6043", "count": 1,
        "targets": "buildings", "ram": True,
    },
    "Варвары": {
        "cost": 5, "hp": 430, "damage": 76, "speed": 48, "range": 24,
        "cooldown": 0.9, "size": 13, "color": "#ba7e50", "count": 3,
    },
    "Элитные варвары": {
        "cost": 6, "hp": 770, "damage": 118, "speed": 54, "range": 26,
        "cooldown": 1.0, "size": 15, "color": "#b45645", "count": 2,
    },
    "Меганайт": {
        "cost": 7, "hp": 1400, "damage": 128, "speed": 28, "range": 30,
        "cooldown": 1.6, "size": 21, "color": "#8d7d70", "count": 1,
        "targets": "buildings", "meganight": True,
    },
    "Принц": {
        "cost": 5, "hp": 750, "damage": 96, "speed": 62, "range": 27,
        "cooldown": 1.4, "size": 17, "color": "#d0b04c", "count": 1,
        "charge": True,
    },
    "Тёмный принц": {
        "cost": 4, "hp": 710, "damage": 86, "speed": 48, "range": 28,
        "cooldown": 1.3, "size": 16, "color": "#654c79", "count": 1,
        "splash": 48,
    },
    "ПЕККА": {
        "cost": 7, "hp": 1500, "damage": 180, "speed": 23, "range": 31,
        "cooldown": 1.8, "size": 22, "color": "#b8a6bd", "count": 1,
    },
    "Мини-ПЕККА": {
        "cost": 4, "hp": 620, "damage": 118, "speed": 48, "range": 25,
        "cooldown": 1.1, "size": 14, "color": "#7087a0", "count": 1,
    },
    "Валькирия": {
        "cost": 4, "hp": 780, "damage": 96, "speed": 53, "range": 27,
        "cooldown": 1.4, "size": 16, "color": "#bd7659", "count": 1,
        "splash": 55,
    },
    "Гарпии": {
        "cost": 3, "hp": 130, "damage": 42, "speed": 70, "range": 28,
        "cooldown": 0.8, "size": 9, "color": "#a2a2c7", "count": 3,
        "flying": True, "can_target_air": True,
    },
    "Адский дракон": {
        "cost": 4, "hp": 620, "damage": 72, "speed": 55, "range": 120,
        "cooldown": 1.2, "size": 16, "color": "#b94f45", "count": 1,
        "flying": True, "can_target_air": True, "splash": 36,
    },
    "Гриф-привидение": {
        "cost": 3, "hp": 210, "damage": 48, "speed": 68, "range": 115,
        "cooldown": 1.0, "size": 11, "color": "#7a72a0", "count": 1,
        "flying": True, "can_target_air": True,
    },
    "Воздушный бомбардир": {
        "cost": 3, "hp": 250, "damage": 82, "speed": 45, "range": 105,
        "cooldown": 1.3, "size": 13, "color": "#d08c56", "count": 1,
        "flying": True, "can_target_air": True, "splash": 32,
    },
    "Солнечный феникс": {
        "cost": 4, "hp": 310, "damage": 64, "speed": 64, "range": 110,
        "cooldown": 1.1, "size": 14, "color": "#ed9a55", "count": 1,
        "flying": True, "can_target_air": True,
    },
    "Хог Райдер": {
        "cost": 4, "hp": 650, "damage": 112, "speed": 68, "range": 26,
        "cooldown": 1.2, "size": 16, "color": "#d59a58", "count": 1,
        "targets": "buildings",
    },
    "Мушкетёр": {
        "cost": 4, "hp": 220, "damage": 66, "speed": 35, "range": 145,
        "cooldown": 1.05, "size": 12, "color": "#936eaa", "count": 1,
        "can_target_air": True,
    },
    "Принцесса": {
        "cost": 3, "hp": 150, "damage": 72, "speed": 40, "range": 155,
        "cooldown": 1.1, "size": 11, "color": "#c8b5df", "count": 1,
        "can_target_air": True, "splash": 30,
    },
    "Баллон": {
        "cost": 5, "hp": 850, "damage": 240, "speed": 38, "range": 28,
        "cooldown": 1.5, "size": 18, "color": "#bb6a65", "count": 1,
        "flying": True, "targets": "buildings",
    },
    "Ведьма": {
        "cost": 5, "hp": 330, "damage": 52, "speed": 37, "range": 115,
        "cooldown": 1.1, "size": 13, "color": "#75508f", "count": 1,
        "can_target_air": True, "spawn_skeletons": True,
    },
    "Ледяной голем": {
        "cost": 2, "hp": 470, "damage": 24, "speed": 25, "range": 25,
        "cooldown": 1.2, "size": 15, "color": "#93cde2", "count": 1,
        "splash": 38,
    },
    "Инферно-дракон": {
        "cost": 4, "hp": 520, "damage": 86, "speed": 48, "range": 125,
        "cooldown": 1.15, "size": 15, "color": "#dc7d43", "count": 1,
        "flying": True, "can_target_air": True,
    },
    "Костяной дракон": {
        "cost": 4, "hp": 390, "damage": 72, "speed": 52, "range": 120,
        "cooldown": 1.2, "size": 15, "color": "#cbd0b5", "count": 1,
        "flying": True, "can_target_air": True, "splash": 26,
    },
    "Королевская принцесса": {
        "cost": 5, "hp": 420, "damage": 74, "speed": 42, "range": 150,
        "cooldown": 1.0, "size": 12, "color": "#dca9ca", "count": 1,
        "flying": True, "can_target_air": True,
    },
}

MEME_CARD_PREFIXES = (
    "Фурри", "Квадробер", "Хоббихорсер", "Скибиди", "Бобр-строитель",
    "Кот-батон", "Сырный фанат", "Пельменный маг", "Ночной курьер",
    "Пиксельный дед", "Гусь-разведчик", "Енот-блогер", "Краб-танцор",
    "Кефирный рыцарь", "Чихуахуа-босс", "Банановый ниндзя",
    "Космо-бариста", "Лиминальный турист", "Жуткий клоун", "Мемный пророк",
)
MEME_CARD_ROLES = (
    "на самокате", "техномаг", "берсерк", "сапёр", "защитник дивана",
    "пицца-рейдер", "повелитель носков", "звёздный стажёр",
    "мастер карате", "босс рейда",
)
MEME_CARD_ARCHETYPES = (
    {"cost": 2, "hp": 30, "damage": 28, "speed": 70, "range": 24,
     "cooldown": 0.72, "size": 8, "color": "#74a96a", "count": 3},
    {"cost": 3, "hp": 170, "damage": 46, "speed": 42, "range": 88,
     "cooldown": 1.0, "size": 11, "color": "#7594b4", "count": 1,
     "can_target_air": True},
    {"cost": 4, "hp": 340, "damage": 70, "speed": 31, "range": 30,
     "cooldown": 1.25, "size": 16, "color": "#b27b55", "count": 1},
    {"cost": 3, "hp": 115, "damage": 34, "speed": 56, "range": 26,
     "cooldown": 0.8, "size": 9, "color": "#a16da6", "count": 2},
    {"cost": 5, "hp": 560, "damage": 88, "speed": 24, "range": 32,
     "cooldown": 1.4, "size": 19, "color": "#877f55", "count": 1,
     "targets": "buildings"},
)
MEME_CARD_COLORS = ("#dc7256", "#688fc1", "#76a866", "#bd8ab0", "#d0a64f")
for index, (prefix, role) in enumerate(
        (prefix, role) for prefix in MEME_CARD_PREFIXES for role in MEME_CARD_ROLES):
    card_name = f"{prefix} {role}"
    stats = MEME_CARD_ARCHETYPES[index % len(MEME_CARD_ARCHETYPES)].copy()
    scale = 0.88 + (index % 5) * 0.06
    stats["hp"] = round(stats["hp"] * scale)
    stats["damage"] = round(stats["damage"] * (1.08 - (index % 5) * 0.04))
    stats["color"] = MEME_CARD_COLORS[index % len(MEME_CARD_COLORS)]
    if "на самокате" in role or "пицца-рейдер" in role:
        stats["hp"] = 84
        stats["count"] = 2
    if prefix == "Хоббихорсер" and stats["cost"] >= 3:
        original_cost = stats["cost"]
        stats["cost"] -= 1
        efficiency_scale = stats["cost"] / original_cost
        stats["hp"] = round(stats["hp"] * efficiency_scale)
        stats["damage"] = round(stats["damage"] * efficiency_scale)
    CARDS[card_name] = stats

CARDS["Фурри-медведь"] = {
    "cost": 5, "hp": 720, "damage": 82, "speed": 28, "range": 30,
    "cooldown": 1.25, "size": 19, "color": "#9b7156", "count": 1,
    "targets": "buildings",
}
CARDS["Фурри-страж"] = {
    "cost": 4, "hp": 620, "damage": 72, "speed": 31, "range": 28,
    "cooldown": 1.2, "size": 17, "color": "#7774a5", "count": 1,
}
CARDS["Хоббихорсер-медведь"] = {
    "cost": 4, "hp": 576, "damage": 66, "speed": 28, "range": 30,
    "cooldown": 1.25, "size": 19, "color": "#a88c62", "count": 1,
    "targets": "buildings",
}
CARDS["Хоббихорсер-боец"] = {
    "cost": 3, "hp": 465, "damage": 54, "speed": 31, "range": 27,
    "cooldown": 1.2, "size": 17, "color": "#87785f", "count": 1,
}

CARDS["67-Мем-стример"] = {
    "cost": 6, "hp": 670, "damage": 67, "speed": 67, "range": 67,
    "cooldown": 1.0, "size": 12, "color": "#67d9ff", "count": 1,
    "flying": True, "can_target_air": True,
}
CARDS["Кринж-кот"] = {
    "cost": 3, "hp": 240, "damage": 42, "speed": 67, "range": 40,
    "cooldown": 0.67, "size": 10, "color": "#e7a9d3", "count": 2,
}
CARDS["Сигма-кракен"] = {
    "cost": 5, "hp": 670, "damage": 67, "speed": 27, "range": 34,
    "cooldown": 1.67, "size": 18, "color": "#8f74cf", "count": 1,
    "splash": 67,
}


def elemental_type(card):
    name = card.lower()
    if any(token in name for token in ("огнен", "инферно", "адский дракон", "феникс")):
        return "fire"
    if any(token in name for token in ("ледян", "снежн")):
        return "ice"
    if any(token in name for token in ("электро", "молни")):
        return "lightning"
    if "кракен" in name:
        return "water"
    return None


RARITY_TYPES = (
    ("Обычная", "#a9adb5"),
    ("Редкая", "#67b46a"),
    ("Эпичная", "#a568bd"),
    ("Сверхредкая", "#df9d45"),
    ("Легендарная", "#dfca58"),
    ("Супергеройская", "#60bfd8"),
)

for card_index, (card_name, card_data) in enumerate(CARDS.items(), start=1):
    rarity_index = (card_index * 5 + len(card_name) * 3) % len(RARITY_TYPES)
    card_data["rarity"] = RARITY_TYPES[rarity_index][0]
    card_data["rarity_color"] = RARITY_TYPES[rarity_index][1]
    card_data["model"] = (card_index * 7 + sum(map(ord, card_name))) % 12

LEGACY_CARDS = [
    "Рыцарь", "Лучницы", "Великан", "Гоблины", "Маг", "Копейщица",
    "Огненный шар", "Лечение", "Страж", "Летучие мыши", "Тролль",
    "Молния", "Арбалетчик", "Голем", "Дракончик", "Ледяной маг",
]


class Tower:
    def __init__(self, x, y, side, crown=False):
        self.x = x
        self.y = y
        self.side = side
        self.crown = crown
        self.is_building = True
        self.flying = False
        self.activated = not crown
        self.lane = 0 if x < 480 else 1
        if crown:
            self.lane = -1
        self.radius = 32 if crown else 25
        self.max_hp = 1600 if crown else 950
        self.hp = self.max_hp
        self.cooldown = random.uniform(0.2, 0.8)


class Unit:
    def __init__(self, x, y, side, card, lane, level=1, stats=None,
                 display_name=None):
        data = stats or CARDS[card]
        self.stats = data
        self.level = level
        self.x = x
        self.y = y
        self.side = side
        self.card = card
        self.display_name = display_name or card
        self.lane = lane
        self.crossed_bridge = False
        self.max_hp = round(data["hp"] * (1 + 0.08 * (level - 1)))
        self.hp = self.max_hp
        self.damage = round(data["damage"] * (1 + 0.07 * (level - 1)))
        self.speed = data["speed"]
        self.range = data["range"]
        self.cooldown = data["cooldown"]
        self.timer = random.uniform(0, data["cooldown"])
        self.size = data["size"]
        self.color = data["color"]
        self.attack_timer = 0
        self.attack_phase = 0
        self.walk_phase = random.uniform(0, math.tau)
        self.slow_timer = 0
        self.is_building = data.get("building", False)
        self.flying = data.get("flying", False)
        self.targets = data.get("targets", "all")
        self.can_target_air = data.get("can_target_air", self.flying)
        self.lifetime = data.get("lifetime")
        self.death_spawn = data.get("death_spawn")


class ClashArena:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Королевская арена")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.resizable(True, True)
        self.root.minsize(768, 480)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.fullscreen = False

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT,
                                highlightthickness=0, bg="#ddd1a2")
        self.canvas.pack(fill="both", expand=True)
        self.canvas_scale_x = 1.0
        self.canvas_scale_y = 1.0
        self.rendered_scale_x = 1.0
        self.rendered_scale_y = 1.0

        self.arena_index = 0
        self.skin_index = 0
        self.best = 0
        self.best_trophies = 0
        self.wins = 0
        self.gold = 120
        self.chests = 1
        self.trophies = 0
        self.battles_played = 0
        self.crowns_earned = 0
        self.upgrades_done = 0
        self.battle_pass_xp = 0
        self.chest_revealed = False
        self.card_levels = {name: 1 for name in CARDS}
        self.unlocked_cards = STARTER_CARDS[:]
        self.battle_deck = STARTER_CARDS[:]
        self.deck_page = 0
        self.collection_page = 0
        self.upgrade_card = STARTER_CARDS[0]
        self.profile_card = None
        self.last_reward = ""
        self.show_hitboxes = False
        self.mouse_x = WIDTH // 2
        self.mouse_y = HEIGHT // 2
        self.screen = "menu"
        self.notice = ""
        self.bot_name = random.choice(BOT_NAMES)
        self.bot_level = random.randint(1, 5)
        self.bot_deck = []
        self.bot_card_levels = {}
        self.furry_vs_horse_side = "furry"
        self.player_expanded_lanes = set()
        self.bot_expanded_lanes = set()
        self.load_save()

        self.running = False
        self.paused = False
        self.mode = "sudden"
        self.selected_card = None
        self.time_left = 180
        self.player_elixir = STARTING_ELIXIR
        self.bot_elixir = STARTING_ELIXIR
        self.deck = self.battle_deck[:]
        self.hand = self.deck[:4]
        self.draw_queue = self.deck[4:]
        self.deck_edit_slot = None
        self.units = []
        self.projectiles = []
        self.effects = []
        self.towers = []
        self.player_crowns = 0
        self.bot_crowns = 0
        self.overtime = False
        self.overtime_left = 60
        self.overtime_drain_side = None
        self.overtime_drain_tick = 0
        self.forced_winner = None
        self.last_tick = 0
        self.loop_token = 0

        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Motion>", self.track_mouse)
        self.canvas.bind("<Configure>", self.resize_canvas)
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<KeyRelease>", lambda event: None)

        self.show_menu()

    def load_save(self):
        try:
            data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
            self.best = int(data.get("best", 0))
            self.wins = int(data.get("wins", 0))
            self.skin_index = max(0, min(len(HERO_SKINS)-1, int(data.get("skin", 0))))
            self.gold = max(0, int(data.get("gold", self.gold)))
            self.chests = max(0, int(data.get("chests", self.chests)))
            self.trophies = max(0, int(data.get("trophies", 0)))
            self.best_trophies = max(
                self.trophies, int(data.get("best_trophies", self.trophies))
            )
            self.arena_index = arena_for_trophies(self.best_trophies)
            self.battles_played = max(0, int(data.get("battles_played", 0)))
            self.crowns_earned = max(0, int(data.get("crowns_earned", 0)))
            self.upgrades_done = max(0, int(data.get("upgrades_done", 0)))
            self.battle_pass_xp = max(0, int(data.get("battle_pass_xp", 0)))
            saved_levels = data.get("card_levels", {})
            if isinstance(saved_levels, dict):
                for name in CARDS:
                    self.card_levels[name] = max(1, min(5, int(saved_levels.get(name, 1))))
            saved_deck = data.get("battle_deck")
            filtered_deck = []
            if isinstance(saved_deck, list):
                filtered_deck = list(dict.fromkeys(
                    name for name in saved_deck if name in CARDS
                ))
            saved_unlocks = data.get("unlocked_cards")
            if isinstance(saved_unlocks, list):
                self.unlocked_cards = list(dict.fromkeys(
                    STARTER_CARDS + [
                        name for name in saved_unlocks
                        if isinstance(name, str) and name in CARDS
                    ]
                ))
            else:
                self.unlocked_cards = list(dict.fromkeys(
                    STARTER_CARDS
                    + (LEGACY_CARDS if isinstance(saved_deck, list) else [])
                    + filtered_deck
                ))
            usable_deck = [
                name for name in filtered_deck if name in self.unlocked_cards
            ]
            if len(usable_deck) == 8:
                self.battle_deck = usable_deck
            self.last_reward = str(data.get("last_reward", ""))
        except (OSError, ValueError, json.JSONDecodeError, TypeError):
            pass

    def save(self):
        try:
            SAVE_FILE.write_text(json.dumps({
                "best": self.best,
                "wins": self.wins,
                "best_trophies": self.best_trophies,
                "skin": self.skin_index,
                "gold": self.gold,
                "chests": self.chests,
                "trophies": self.trophies,
                "battles_played": self.battles_played,
                "crowns_earned": self.crowns_earned,
                "upgrades_done": self.upgrades_done,
                "battle_pass_xp": self.battle_pass_xp,
                "card_levels": self.card_levels,
                "unlocked_cards": self.unlocked_cards,
                "battle_deck": self.battle_deck,
                "last_reward": self.last_reward,
            }), encoding="utf-8")
        except OSError:
            pass

    def quit(self):
        self.save()
        self.running = False
        self.root.destroy()

    def key_press(self, event):
        if event.keysym.lower() == "escape" and self.running:
            self.paused = not self.paused
        if event.keysym.lower() == "h" and self.running:
            self.show_hitboxes = not self.show_hitboxes
        if self.running and not self.paused and event.char.isdigit():
            index = int(event.char) - 1
            if 0 <= index < len(self.hand):
                self.selected_card = self.hand[index]

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        return "break"

    def clear_canvas(self):
        self.canvas.delete("all")
        self.rendered_scale_x = 1.0
        self.rendered_scale_y = 1.0

    def apply_canvas_scale(self):
        scale_x = self.canvas_scale_x / self.rendered_scale_x
        scale_y = self.canvas_scale_y / self.rendered_scale_y
        if scale_x != 1 or scale_y != 1:
            self.canvas.scale("all", 0, 0, scale_x, scale_y)
        self.rendered_scale_x = self.canvas_scale_x
        self.rendered_scale_y = self.canvas_scale_y

    def resize_canvas(self, event):
        self.canvas_scale_x = max(1, event.width) / WIDTH
        self.canvas_scale_y = max(1, event.height) / HEIGHT
        if self.screen == "game":
            self.draw()
        else:
            self.apply_canvas_scale()

    def design_point(self, x, y):
        return x / self.canvas_scale_x, y / self.canvas_scale_y

    def show_menu(self):
        self.running = False
        self.paused = False
        self.loop_token += 1
        self.screen = "menu"
        arena = ARENAS[self.arena_index]
        self.canvas.configure(bg=arena[1])
        self.clear_canvas()

        self.canvas.create_text(480, 115, text="КОРОЛЕВСКАЯ АРЕНА",
                                fill="#fff4c7", font=("TkDefaultFont", 36, "bold"))
        self.canvas.create_text(480, 172,
                                text=f"КУБКИ  {self.trophies}    •    ПОБЕДЫ  {self.wins}    •    ЛУЧШИЙ СЧЁТ  {self.best}",
                                fill=arena[3], font=("TkDefaultFont", 12, "bold"))
        self.canvas.create_rectangle(245, 220, 715, 430, fill="#29352d",
                                     outline="#d8b36a", width=4)
        self.canvas.create_text(480, 265, text=f"АРЕНА: {arena[0]}",
                                fill="#f3d9a1", font=("TkDefaultFont", 17, "bold"))
        self.canvas.create_text(480, 300,
                                text=f"РЕЖИМ: {self.mode_label()}  •  КОЛОДА: {len(self.battle_deck)}/8",
                                fill="#e9e2c5", font=("TkDefaultFont", 11, "bold"))
        self.button(320, 335, 640, 405, "ВЫБРАТЬ РЕЖИМ", "#f0ca6c", "#342c23",
                    self.show_match_setup)
        self.canvas.create_text(480, 465, text="F11 — полный экран / оконный режим",
                                fill="#fff4c7", font=("TkDefaultFont", 11, "bold"))
        self.bottom_nav("")
        self.apply_canvas_scale()

    def bottom_nav(self, current):
        tabs = [
            ("БОЙ", "battle", self.show_match_setup),
            ("АРЕНЫ", "arenas", self.show_arenas),
            ("КОЛОДА", "deck", self.show_deck),
            ("УЛУЧШЕНИЯ", "collection", self.show_collection),
            ("МАГАЗИН", "shop", self.show_shop),
            ("ЦЕЛИ", "achievements", self.show_achievements),
        ]
        for index, (label, name, command) in enumerate(tabs):
            x1 = 4 + index * 159
            color = "#f0ca6c" if name == current else "#c5d5e0"
            self.button(x1, 551, x1+153, 594, label, color, "#342c23",
                        command, outline="#fff0a8" if name == current else "#7c806e")

    def show_arenas(self):
        self.running = False
        self.paused = False
        self.loop_token += 1
        self.screen = "arenas"
        arena = ARENAS[self.arena_index]
        self.canvas.configure(bg=arena[1])
        self.clear_canvas()
        self.canvas.create_text(480, 34, text="ДОРОГА АРЕН",
                                fill="#fff1c4", font=("TkDefaultFont", 25, "bold"))
        next_threshold = (self.arena_index + 1) * ARENA_TROPHY_STEP
        progress = min(1, self.best_trophies / max(1, next_threshold))
        self.canvas.create_text(480, 68,
                                text=f"{self.best_trophies} / {next_threshold} кубков • {arena[0]}",
                                fill=arena[3], font=("TkDefaultFont", 12, "bold"))
        self.canvas.create_rectangle(190, 88, 770, 101, fill="#292722",
                                     outline="#e3d3a9", width=1)
        self.canvas.create_rectangle(192, 90, 192+576*progress, 99,
                                     fill="#dfba56", outline="")

        for offset in range(-2, 3):
            rank = self.arena_index + offset
            if not 0 <= rank < len(ARENAS):
                continue
            name, ground, river, trim = ARENAS[rank]
            y = 132 + (offset + 2) * 73
            unlocked = rank <= self.arena_index
            fill = "#354438" if unlocked else "#323135"
            self.canvas.create_rectangle(170, y, 790, y+62, fill=fill,
                                         outline=trim, width=2)
            self.canvas.create_text(194, y+20, anchor="w", text=name,
                                    fill=trim, font=("TkDefaultFont", 11, "bold"))
            status = ("ОТКРЫТА" if rank < self.arena_index else "ТЕКУЩАЯ АРЕНА") if unlocked else (
                f"{rank * ARENA_TROPHY_STEP} кубков • сундук, золото и карта"
            )
            self.canvas.create_text(194, y+43, anchor="w", text=status,
                                    fill="#e6dfc9", font=("TkDefaultFont", 9))
            self.canvas.create_rectangle(720, y+9, 773, y+53, fill=ground,
                                         outline=trim, width=2)
            self.canvas.create_line(724, y+43, 769, y+17, fill=river, width=7)
        self.bottom_nav("arenas")
        self.apply_canvas_scale()

    def show_appearance(self):
        self.running = False
        self.paused = False
        self.loop_token += 1
        self.screen = "appearance"
        arena = ARENAS[self.arena_index]
        self.canvas.configure(bg=arena[1])
        self.clear_canvas()
        self.canvas.create_text(480, 40, text="ОБЛИКИ", fill="#fff4c7",
                                font=("TkDefaultFont", 26, "bold"))
        self.canvas.create_text(480, 76, text="СКИН БАШНИ И ГЕРОЯ", fill="#fff4c7",
                                font=("TkDefaultFont", 13, "bold"))
        for i, (name, color) in enumerate(HERO_SKINS):
            x = 42 + (i % 3) * 304
            y = 110 + (i // 3) * 54
            outline = "#f3d27a" if i == self.skin_index else "#727866"
            self.button(x, y, x+286, y+42, name, color, "#31372d",
                        lambda idx=i: self.select_skin(idx), outline)
        self.button(350, 300, 610, 345,
                    "РЕЖИМ: " + self.mode_label(),
                    "#ddd9ae", "#3b3022", self.toggle_mode)
        self.button(350, 360, 610, 405, "НАЗАД В КРЕПОСТЬ", "#f0ca6c", "#342c23",
                    self.show_menu)
        self.apply_canvas_scale()

    def show_deck(self):
        self.running = False
        self.paused = False
        self.loop_token += 1
        self.screen = "deck"
        self.canvas.configure(bg="#26352e")
        self.clear_canvas()
        self.canvas.create_text(480, 30, text="СОЗДАТЬ КОЛОДУ",
                                fill="#fff1c4", font=("TkDefaultFont", 26, "bold"))
        average_cost = sum(CARDS[card]["cost"] for card in self.battle_deck)/max(1, len(self.battle_deck))
        self.canvas.create_text(480, 58, text=f"В КОЛОДЕ: {len(self.battle_deck)}/8  •  СРЕДНЯЯ СТОИМОСТЬ: {average_cost:.1f}",
                                fill="#c6d6ad", font=("TkDefaultFont", 10, "bold"))

        for index, card in enumerate(self.battle_deck):
            x = 35 + (index % 4) * 225
            y = 78 + (index // 4) * 72
            self.draw_card_tile(x, y, 210, 62, card,
                                lambda slot=index: self.select_deck_slot(slot),
                                in_deck=True, selected=index == self.deck_edit_slot)

        self.canvas.create_line(35, 229, 925, 229, fill="#7b8865", width=2)
        self.canvas.create_text(480, 246, text="КОЛЛЕКЦИЯ — ОТКРЫТЫЕ МОЖНО ДОБАВИТЬ, ЗАКРЫТЫЕ ИЩИ В СУНДУКАХ",
                                fill="#e6dcb8", font=("TkDefaultFont", 11, "bold"))
        collection = [name for name in CARDS if name not in self.battle_deck]
        page_count = max(1, (len(collection) + 11) // 12)
        self.deck_page = max(0, min(self.deck_page, page_count - 1))
        page_cards = collection[self.deck_page*12:(self.deck_page+1)*12]
        for index, card in enumerate(page_cards):
            x = 35 + (index % 4) * 225
            y = 263 + (index // 4) * 78
            unlocked = card in self.unlocked_cards
            self.draw_card_tile(x, y, 210, 72, card,
                                (lambda name=card: self.add_to_deck(name)) if unlocked else None,
                                in_deck=False, locked=not unlocked)
        if not collection:
            self.canvas.create_text(480, 330, text="Все открытые карты уже в колоде.",
                                    fill="#c6d6ad", font=("TkDefaultFont", 11))
        if page_count > 1:
            self.button(90, 500, 300, 536, "◀ НАЗАД",
                        "#c5d5e0" if self.deck_page > 0 else "#696a60", "#342c23",
                        lambda: self.change_deck_page(-1))
            self.canvas.create_text(480, 518, text=f"{self.deck_page+1}/{page_count}",
                                    fill="#fff1c4", font=("TkDefaultFont", 10, "bold"))
            self.button(660, 500, 870, 536, "ДАЛЕЕ ▶",
                        "#c5d5e0" if self.deck_page + 1 < page_count else "#696a60",
                        "#342c23", lambda: self.change_deck_page(1))
        if self.notice:
            self.canvas.create_text(480, 540, text=self.notice, fill="#ffcf78",
                                    font=("TkDefaultFont", 10, "bold"))
        self.bottom_nav("deck")
        self.apply_canvas_scale()

    def draw_card_tile(self, x, y, width, height, card, command, in_deck,
                       selected=False, locked=False):
        data = CARDS[card]
        level = self.card_levels.get(card, 1)
        base = "#eee2b8" if in_deck else "#d7d4be"
        if locked:
            base = "#98968a"
        border = "#f4ce69" if selected else ("#f4ce69" if in_deck else "#88917b")
        tile = self.canvas.create_rectangle(x, y, x+width, y+height,
                                            fill=base, outline=border, width=4 if selected else 2)
        icon_x, icon_y = x+30, y+height/2
        icon = self.canvas.create_oval(icon_x-18, icon_y-18, icon_x+18, icon_y+18,
                                       fill=data["color"], outline="#594c3d", width=2)
        if data.get("spell"):
            symbol = self.canvas.create_polygon(
                icon_x, icon_y-14, icon_x+5, icon_y-3,
                icon_x+13, icon_y-2, icon_x+5, icon_y+4,
                icon_x+8, icon_y+14, icon_x-2, icon_y+6,
                icon_x-12, icon_y+11, icon_x-6, icon_y+1,
                icon_x-11, icon_y-6, icon_x-2, icon_y-5,
                fill="#fff2c4", outline="")
        else:
            symbol = self.canvas.create_oval(icon_x-6, icon_y-9, icon_x+6, icon_y+9,
                                             fill="#e8c793", outline="#514738")
            weapon = self.canvas.create_line(icon_x, icon_y-2, icon_x+12, icon_y-12,
                                             fill="#e8e0c3", width=3)
        title = self.canvas.create_text(x+58, y+17, anchor="w", text=card,
                                        fill="#342e28", font=("TkDefaultFont", 10, "bold"))
        cost = self.canvas.create_oval(x+width-36, y+5, x+width-8, y+33,
                                       fill="#b14eaa", outline="#633a76", width=2)
        cost_text = self.canvas.create_text(x+width-22, y+19, text=str(data["cost"]),
                                           fill="#fff4ff", font=("TkDefaultFont", 10, "bold"))
        if locked:
            detail_text = "Закрыта • сундук или покупка в коллекции"
        elif card == "Лечение":
            detail_text = f"Ур. {level}  •  заклинание  •  лечение 160"
        elif card == "Молния":
            detail_text = f"Ур. {level}  •  закл.  •  {data['damage']} урона, 3 цели"
        elif data.get("spell_kind") == "barrel":
            detail_text = "Заклинание • бочка летит и выпускает 3 гоблинов"
        elif data.get("spell"):
            detail_text = f"Ур. {level}  •  заклинание  •  урон {data['damage']}"
        elif data.get("building"):
            detail_text = f"Здание  •  HP {data['hp']}  •  стоит {data['lifetime']} с"
        elif data.get("targets") == "buildings":
            detail_text = f"Танк  •  только здания  •  HP {data['hp']}"
        elif data.get("flying"):
            detail_text = f"Воздух  •  HP {data['hp']}  •  урон {data['damage']}"
        else:
            detail_text = f"Ур. {level}  •  {data['rarity']}  •  HP {data['hp']}  •  урон {data['damage']}"
        detail = self.canvas.create_text(x+58, y+40,
                                         anchor="w",
                                         text=detail_text,
                                         fill="#625b4b", font=("TkDefaultFont", 8))
        tile_items = [tile, icon, symbol, title, cost, cost_text, detail]
        if not data.get("spell"):
            tile_items.append(weapon)
        if command is not None:
            for item in tile_items:
                self.canvas.tag_bind(item, "<Button-1>",
                                     lambda event, cmd=command: (cmd(), "break")[1])

    def change_deck_page(self, delta):
        page_count = max(1, (len(CARDS) - len(self.battle_deck) + 11) // 12)
        self.deck_page = max(0, min(page_count - 1, self.deck_page + delta))
        self.show_deck()

    def select_deck_slot(self, index):
        self.deck_edit_slot = index
        self.notice = "Теперь выбери карту из коллекции для замены."
        self.show_deck()

    def add_to_deck(self, card):
        if card not in self.unlocked_cards:
            self.notice = "Сначала найди карту в сундуке или купи её в коллекции."
        elif self.deck_edit_slot is not None:
            if card in self.battle_deck and self.battle_deck[self.deck_edit_slot] != card:
                self.notice = "В колоде не может быть двух одинаковых карт."
                self.show_deck()
                return
            self.battle_deck[self.deck_edit_slot] = card
            self.deck_edit_slot = None
            self.notice = f"«{card}» добавлена в колоду."
        elif len(self.battle_deck) < 8:
            if card in self.battle_deck:
                self.notice = "Эта карта уже в колоде."
            else:
                self.battle_deck.append(card)
        else:
            self.notice = "Сначала нажми на карту в колоде, которую хочешь заменить."
        self.save()
        self.show_deck()

    def show_chests(self):
        self.running = False
        self.paused = False
        self.loop_token += 1
        self.screen = "chests"
        arena = ARENAS[self.arena_index]
        self.canvas.configure(bg=arena[1])
        self.clear_canvas()
        self.canvas.create_text(480, 50, text="СУНДУЧНАЯ", fill="#fff1c4",
                                font=("TkDefaultFont", 30, "bold"))
        self.canvas.create_text(480, 84, text="НАГРАДЫ ЗА ПОБЕДЫ НА АРЕНЕ",
                                fill=arena[3], font=("TkDefaultFont", 11, "bold"))
        self.draw_chest(480, 230, opened=self.chest_revealed)
        self.canvas.create_text(480, 345, text=f"СУНДУКОВ: {self.chests}     •     ЗОЛОТА: {self.gold}",
                                fill="#fff1c4", font=("TkDefaultFont", 14, "bold"))
        if self.last_reward:
            self.canvas.create_text(480, 380, text=f"ПОСЛЕДНЯЯ НАГРАДА: {self.last_reward}",
                                    fill="#f3d37a", font=("TkDefaultFont", 10, "bold"))
        self.button(340, 405, 620, 455, "ОТКРЫТЬ СУНДУК", "#f0ca6c", "#342c23",
                    self.open_chest, outline="#fff0a8")
        self.button(340, 463, 620, 510, "КУПИТЬ СУНДУК  •  100 ЗОЛОТА",
                    "#d6c6e8", "#342c23", self.buy_chest)
        self.bottom_nav("shop")
        self.apply_canvas_scale()

    def show_shop(self):
        self.running = False
        self.paused = False
        self.loop_token += 1
        self.screen = "shop"
        arena = ARENAS[self.arena_index]
        self.canvas.configure(bg=arena[1])
        self.clear_canvas()
        self.canvas.create_text(480, 55, text="ПРИЛАВОК КРЕПОСТИ",
                                fill="#fff1c4", font=("TkDefaultFont", 30, "bold"))
        self.canvas.create_text(480, 95, text=f"ЗОЛОТО: {self.gold}",
                                fill=arena[3], font=("TkDefaultFont", 14, "bold"))
        self.canvas.create_rectangle(270, 130, 690, 495, fill="#29352d",
                                     outline="#d8b36a", width=4)
        self.draw_chest(480, 245, opened=False)
        self.canvas.create_text(480, 345, text="СУНДУК С КАРТАМИ",
                                fill="#f3d9a1", font=("TkDefaultFont", 19, "bold"))
        self.canvas.create_text(480, 378, text="Открой новую карту или получи золото.",
                                fill="#e9e2c5", font=("TkDefaultFont", 11))
        self.button(340, 395, 620, 438, f"ОТКРЫТЬ СУНДУКИ  •  {self.chests}",
                    "#d6c6e8", "#342c23", self.show_chests)
        self.button(340, 444, 620, 487, "КУПИТЬ СУНДУК  •  100 ЗОЛОТА",
                    "#f0ca6c", "#342c23", self.buy_chest)
        self.bottom_nav("shop")
        self.apply_canvas_scale()

    def show_collection(self):
        self.running = False
        self.paused = False
        self.loop_token += 1
        self.screen = "collection"
        self.canvas.configure(bg="#26352e")
        self.clear_canvas()
        self.canvas.create_text(480, 35, text="КОЛЛЕКЦИЯ И УЛУЧШЕНИЯ",
                                fill="#fff1c4", font=("TkDefaultFont", 25, "bold"))
        self.canvas.create_text(850, 35, text=f"ЗОЛОТО: {self.gold}",
                                fill="#f3d37a", font=("TkDefaultFont", 11, "bold"))
        rarity_price_text = " | ".join(
            f"{rarity}: {CARD_UNLOCK_COSTS[rarity]} золота"
            for rarity in ("Обычная", "Редкая", "Эпичная",
                           "Сверхредкая", "Легендарная", "Супергеройская")
        )
        self.canvas.create_text(480, 60, text=rarity_price_text,
                                fill="#d9d1b3", font=("TkDefaultFont", 8, "bold"))
        upgrade_price_text = "Ул. (база × уровень): " + " | ".join(
            f"{rarity}: {CARD_UPGRADE_COSTS[rarity]} золота"
            for rarity in ("Обычная", "Редкая", "Эпичная",
                           "Сверхредкая", "Легендарная", "Супергеройская")
        )
        self.canvas.create_text(480, 69, text=upgrade_price_text,
                                fill="#c8bda0", font=("TkDefaultFont", 7, "bold"))
        cards_per_page = 20
        page_count = max(1, (len(CARDS) + cards_per_page - 1) // cards_per_page)
        self.collection_page = max(0, min(self.collection_page, page_count - 1))
        page_cards = list(CARDS)[
            self.collection_page * cards_per_page:
            (self.collection_page + 1) * cards_per_page
        ]
        for index, card in enumerate(page_cards):
            x = 30 + (index % 4) * 225
            y = 72 + (index // 4) * 57
            unlocked = card in self.unlocked_cards
            fill = "#d9d1b3" if unlocked else "#858578"
            outline = "#f3ca6b" if card == self.upgrade_card else "#776e58"
            self.canvas.create_rectangle(x, y, x+220, y+49, fill=fill,
                                         outline=outline, width=3 if card == self.upgrade_card else 1)
            level = self.card_levels.get(card, 1)
            status = f"{CARDS[card]['rarity']} • Ур.{level}"
            if not unlocked:
                status = (
                    f"ЗАКРЫТА • {CARDS[card]['rarity']} • "
                    f"{card_unlock_cost(card)} золота или сундук"
                )
            self.canvas.create_text(x+8, y+14, anchor="w", text=card,
                                    fill="#302d26", font=("TkDefaultFont", 9, "bold"))
            self.canvas.create_text(x+8, y+34, anchor="w", text=status,
                                    fill="#5c5547", font=("TkDefaultFont", 8))
            for item in self.canvas.find_overlapping(x, y, x+220, y+49):
                self.canvas.tag_bind(
                    item, "<Button-1>",
                    lambda event, name=card: self.select_upgrade_card(name),
                )

        if page_count > 1:
            self.button(100, 405, 300, 441, "◀ НАЗАД",
                        "#c5d5e0" if self.collection_page > 0 else "#696a60",
                        "#342c23", lambda: self.change_collection_page(-1))
            self.canvas.create_text(480, 423,
                                    text=f"СТРАНИЦА {self.collection_page + 1}/{page_count}",
                                    fill="#fff1c4", font=("TkDefaultFont", 10, "bold"))
            self.button(660, 405, 860, 441, "ДАЛЕЕ ▶",
                        "#c5d5e0" if self.collection_page + 1 < page_count else "#696a60",
                        "#342c23", lambda: self.change_collection_page(1))

        selected = self.upgrade_card
        if selected in CARDS:
            level = self.card_levels.get(selected, 1)
            gold_cost = card_upgrade_cost(selected, level)
            if selected in self.unlocked_cards:
                detail = f"{selected} • уровень {level} • улучшение за {gold_cost} золота"
                self.button(760, 445, 910, 500, "ПРОФИЛЬ",
                            "#b9d8ca", "#342c23",
                            lambda name=selected: self.show_card_profile(name),
                            outline="#e6f1dd", width=2)
            else:
                unlock_cost = card_unlock_cost(selected)
                detail = f"{selected} • {CARDS[selected]['rarity']} • купить за {unlock_cost} золота или найти в сундуке"
            self.canvas.create_text(480, 405, text=detail, fill="#fff1c4",
                                    font=("TkDefaultFont", 10, "bold"))
            if selected not in self.unlocked_cards:
                unlock_cost = card_unlock_cost(selected)
                can_buy = self.gold >= unlock_cost
                button_text = (
                    f"КУПИТЬ КАРТУ • {unlock_cost} ЗОЛОТА"
                    if can_buy else f"НУЖНО {unlock_cost} ЗОЛОТА"
                )
                self.button(330, 465, 630, 521, button_text,
                            "#f0ca6c" if can_buy else "#9c9b8c",
                            "#342c23", self.buy_selected_card)
                self.bottom_nav("collection")
                self.apply_canvas_scale()
                return
            can_upgrade = (
                selected in self.unlocked_cards and level < 5
                and self.gold >= gold_cost
            )
            button_text = (
                "УЛУЧШИТЬ КАРТУ" if can_upgrade
                else f"НУЖНО {gold_cost} ЗОЛОТА"
            )
            if level >= 5:
                button_text = "МАКСИМАЛЬНЫЙ УРОВЕНЬ"
            self.button(330, 465, 630, 521, button_text,
                        "#f0ca6c" if can_upgrade else "#9c9b8c",
                        "#342c23", self.upgrade_selected_card)
        self.bottom_nav("collection")
        self.apply_canvas_scale()

    def card_story(self, card):
        data = CARDS[card]
        if card.startswith(tuple(MEME_CARD_PREFIXES)):
            return (f"{card} появился в Проклятом мем-доме и стал легендой "
                    "после единственной победы над тринадцатой чаинкой.")
        if "67-Мем" in card:
            return "Этот стример зашёл в арене ровно на 67-й секунде и больше не остановился."
        if "Кринж-кот" in card:
            return "Кот прошёл три арены молча, но первый мяук заставил всех боевые башни дрожать."
        if "Сигма-кракен" in card:
            return "Кракен живёт там, куда не доходит эликсир. Никогда не спешит и всегда наносит урон ровно в 67."
        return (f"{card} защищает дорожки с тех пор, как первая корона появилась "
                "над Королевским замком. Каждый бой его история дополняется новой победой.")

    def character_skin_style(self, card, data):
        model = data.get("model", 0)
        seed = sum(map(ord, card))
        palette = ("#e4c56f", "#6ed3d7", "#e78c63", "#c296e5",
                   "#a6d77c", "#f0a3b8", "#f0e5c4", "#79a8ed")
        accent = palette[(seed + model*3) % len(palette)]
        skin_palette = ("#e8c793", "#d79e78", "#efcfaa", "#a96f58", "#d7b1a0")
        skin = skin_palette[seed % len(skin_palette)]
        return accent, skin, (seed + model*3) % 6, (seed + model) % 6

    def draw_character_face(self, card, data, x, y, size):
        if size < 9:
            return
        accent, skin, face_style, head_style = self.character_skin_style(card, data)
        line_width = max(1, round(size / 14))
        self.canvas.create_oval(x-size*.48, y-size*.82,
                    x+size*.48, y+size*.14,
                    fill=skin, outline="#594638", width=line_width)
        hat_top = y-size*.98
        if head_style == 0:
            self.canvas.create_rectangle(x-size*.3, y-size*.91,
                                         x+size*.3, y-size*.72,
                                         fill=accent, outline="#423a32", width=line_width)
            self.canvas.create_line(x-size*.38, y-size*.72,
                                    x+size*.38, y-size*.72,
                                    fill="#eadbb2", width=line_width)
        elif head_style == 1:
            self.canvas.create_oval(x-size*.19, hat_top,
                                    x+size*.19, y-size*.63,
                                    fill=accent, outline="#423a32", width=line_width)
        elif head_style == 2:
            self.canvas.create_rectangle(x-size*.43, y-size*.78,
                                         x+size*.43, y-size*.65,
                                         fill=accent, outline="#423a32", width=line_width)
            self.canvas.create_line(x-size*.35, y-size*.65,
                                    x+size*.35, y-size*.65,
                                    fill="#eadbb2", width=line_width)
        elif head_style == 3:
            self.canvas.create_arc(x-size*.42, y-size*.98,
                                   x+size*.42, y-size*.35,
                                   start=0, extent=180, style="arc",
                                   outline=accent, width=max(2, line_width+1))
        elif head_style == 4:
            self.canvas.create_oval(x-size*.36, y-size*.9,
                                    x+size*.36, y-size*.66,
                                    fill="#55443d", outline=accent, width=line_width)
            self.canvas.create_line(x-size*.35, y-size*.7,
                                    x+size*.35, y-size*.7,
                                    fill="#eadbb2", width=line_width)
        else:
            self.canvas.create_line(x-size*.38, y-size*.72,
                                    x+size*.38, y-size*.72,
                                    fill=accent, width=max(2, line_width+1))
            self.canvas.create_oval(x-size*.06, hat_top,
                                    x+size*.06, y-size*.82,
                                    fill="#eadbb2", outline=accent, width=1)

        eye_y = y-size*.53
        eye_gap = size*.18
        eye_radius = max(1, size*.055)
        if face_style == 0:
            for direction in (-1, 1):
                eye_x = x+direction*eye_gap
                self.canvas.create_oval(eye_x-eye_radius*1.35, eye_y-eye_radius*1.5,
                                        eye_x+eye_radius*1.35, eye_y+eye_radius*1.5,
                                        fill="#fff1d2", outline="#342e28", width=1)
                self.canvas.create_oval(eye_x-eye_radius*.4, eye_y-eye_radius*.8,
                                        eye_x+eye_radius*.5, eye_y+eye_radius*.8,
                                        fill="#24201e", outline="")
        elif face_style == 1:
            for direction in (-1, 1):
                self.canvas.create_line(x+direction*size*.29, eye_y-size*.09,
                                        x+direction*size*.08, eye_y-size*.03,
                                        fill="#342e28", width=line_width+1)
            self.canvas.create_line(x-size*.1, y-size*.27,
                                    x+size*.1, y-size*.27,
                                    fill="#754c43", width=line_width)
        elif face_style == 2:
            for direction in (-1, 1):
                eye_x = x+direction*eye_gap
                self.canvas.create_rectangle(eye_x-size*.11, eye_y-size*.07,
                                             eye_x+size*.11, eye_y+size*.07,
                                             outline=accent, width=line_width+1)
            self.canvas.create_line(x-size*.07, eye_y,
                                    x+size*.07, eye_y,
                                    fill=accent, width=line_width)
        elif face_style == 3:
            self.canvas.create_rectangle(x-size*.34, eye_y-size*.06,
                                         x+size*.34, eye_y+size*.09,
                                         fill="#55443d", outline=accent, width=line_width)
        elif face_style == 4:
            eye_x = x-eye_gap
            self.canvas.create_oval(eye_x-eye_radius, eye_y-eye_radius,
                                    eye_x+eye_radius, eye_y+eye_radius,
                                    fill="#fff1d2", outline="#342e28")
            self.canvas.create_line(x+eye_gap, eye_y-size*.08,
                                    x+eye_gap, eye_y+size*.08,
                                    fill="#342e28", width=line_width+1)
            self.canvas.create_line(x-size*.32, eye_y+size*.16,
                                    x-size*.08, eye_y-size*.04,
                                    fill=accent, width=line_width+1)
        else:
            self.canvas.create_oval(x-eye_gap-eye_radius, eye_y-eye_radius,
                                    x-eye_gap+eye_radius, eye_y+eye_radius,
                                    fill="#24201e", outline="")
            self.canvas.create_line(x+eye_gap-size*.06, eye_y,
                                    x+eye_gap+size*.06, eye_y,
                                    fill="#24201e", width=line_width+1)
            self.canvas.create_arc(x-size*.12, y-size*.3,
                                   x+size*.12, y-size*.15,
                                   start=190, extent=160, style="arc",
                                   outline="#754c43", width=line_width)

    def draw_character_texture(self, card, data, x, y, size):
        model = data.get("model", 0)
        color, _, _, _ = self.character_skin_style(card, data)
        style = model % 5
        line_width = max(1, round(size / 18))
        chest_top = y - size*.12
        chest_bottom = y + size*.3
        self.canvas.create_polygon(x-size*.2, chest_top,
                                   x+size*.2, chest_top,
                                   x+size*.18, y+size*.2,
                                   x, chest_bottom,
                                   x-size*.18, y+size*.2,
                                   fill=data["color"], outline=color, width=line_width)
        if style == 0:
            for offset in (0, .13):
                self.canvas.create_line(x-size*.13, y+size*offset,
                                        x+size*.13, y+size*offset,
                                        fill=color, width=line_width)
        elif style == 1:
            self.canvas.create_polygon(x, y-size*.04,
                                       x+size*.12, y+size*.09,
                                       x, y+size*.22,
                                       x-size*.12, y+size*.09,
                                       fill=color, outline="#342e28", width=line_width)
            for rivet_x in (-.15, .15):
                self.canvas.create_oval(x+size*rivet_x-size*.025, y+size*.08-size*.025,
                                        x+size*rivet_x+size*.025, y+size*.08+size*.025,
                                        fill="#f2dca0", outline="#342e28", width=line_width)
        elif style == 2:
            for dot_y in (0, .12, .24):
                for dot_x in (-.1, .1):
                    self.canvas.create_oval(x+size*dot_x-size*.025,
                                            y+size*dot_y-size*.025,
                                            x+size*dot_x+size*.025,
                                            y+size*dot_y+size*.025,
                                            fill=color, outline="")
        elif style == 3:
            for offset in (-.08, .08):
                self.canvas.create_line(x+size*offset, y-size*.02,
                                        x+size*offset, y+size*.23,
                                        fill=color, width=line_width)
        else:
            self.canvas.create_rectangle(x-size*.1, y-size*.02,
                                         x+size*.1, y+size*.2,
                                         outline=color, width=line_width)
            self.canvas.create_line(x-size*.07, y+size*.09,
                                    x+size*.07, y+size*.09,
                                     fill=color, width=line_width)

    def draw_profile_weapon(self, x, y, size, color, direction, style, ranged):
        hand_x = x + direction*size*.38
        hand_y = y + size*.2
        tip_x = x + direction*size*1.28
        tip_y = y - size*.72
        shaft_width = max(1, round(size/8))
        detail_width = max(1, round(size/12))
        if ranged and style == 0:
            left, right = sorted((hand_x, tip_x))
            self.canvas.create_arc(left, y-size*.95, right, y+size*.38,
                                   start=285 if direction > 0 else 105,
                                   extent=150, style="arc", outline=color, width=shaft_width)
            self.canvas.create_line(hand_x, y-size*.8, hand_x, y+size*.3,
                                    fill="#eee3bd", width=1)
        elif ranged and style == 1:
            self.canvas.create_line(hand_x, hand_y, tip_x, tip_y,
                                    fill="#725338", width=shaft_width)
            self.canvas.create_line(hand_x, hand_y-size*.18,
                                    hand_x+direction*size*.5, hand_y-size*.18,
                                    fill=color, width=detail_width)
            self.canvas.create_line(hand_x, hand_y+size*.18,
                                    hand_x+direction*size*.5, hand_y+size*.18,
                                    fill=color, width=detail_width)
        elif ranged and style in (2, 3):
            self.canvas.create_line(hand_x, hand_y, tip_x, tip_y,
                                    fill="#725338", width=shaft_width)
            self.canvas.create_oval(tip_x-size*.12, tip_y-size*.12,
                                    tip_x+size*.12, tip_y+size*.12,
                                    fill=color, outline="#fff0b4", width=detail_width)
            self.canvas.create_line(tip_x-size*.22, tip_y,
                                    tip_x+size*.22, tip_y,
                                    fill="#fff0b4", width=1)
        elif style == 0:
            self.canvas.create_polygon(hand_x-direction*size*.08, hand_y+size*.08,
                                       hand_x+direction*size*.08, hand_y-size*.08,
                                       tip_x, tip_y,
                                       hand_x-direction*size*.04, hand_y+size*.16,
                                       fill="#d9e3e3", outline="#514638", width=1)
            self.canvas.create_line(hand_x-direction*size*.18, hand_y+size*.1,
                                    hand_x+direction*size*.18, hand_y-size*.1,
                                    fill=color, width=detail_width)
        elif style == 1:
            self.canvas.create_line(hand_x, hand_y, tip_x, tip_y,
                                    fill="#725338", width=shaft_width)
            self.canvas.create_polygon(tip_x-direction*size*.38, tip_y+size*.18,
                                       tip_x, tip_y-size*.2,
                                       tip_x+direction*size*.16, tip_y+size*.2,
                                       fill=color, outline="#514638", width=detail_width)
        elif style == 2:
            self.canvas.create_line(hand_x, hand_y, tip_x, tip_y,
                                    fill="#725338", width=shaft_width)
            self.canvas.create_rectangle(tip_x-direction*size*.24, tip_y-size*.18,
                                         tip_x+direction*size*.24, tip_y+size*.12,
                                         fill=color, outline="#514638", width=detail_width)
        elif style == 3:
            self.canvas.create_line(hand_x, hand_y, tip_x, tip_y,
                                    fill="#725338", width=shaft_width)
            self.canvas.create_oval(tip_x-size*.16, tip_y-size*.16,
                                    tip_x+size*.16, tip_y+size*.16,
                                    fill=color, outline="#fff0b4", width=detail_width)
        else:
            self.canvas.create_line(hand_x, hand_y, tip_x, tip_y,
                                    fill="#725338", width=shaft_width)
            self.canvas.create_polygon(tip_x-direction*size*.13, tip_y+size*.12,
                                       tip_x, tip_y-size*.25,
                                       tip_x+direction*size*.13, tip_y+size*.12,
                                       fill="#d9e3e3", outline="#514638")

    def draw_character_profile(self, card, level):
        if card not in self.unlocked_cards:
            return
        data = CARDS[card]
        model = data.get("model", 0)
        rarity_color = data.get("rarity_color", "#a9adb5")
        x, y = 210, 300
        size = 34
        seed = sum(map(ord, card))
        accent, skin, face_style, head_style = self.character_skin_style(card, data)
        self.canvas.create_oval(x-size-12, y+size+3, x+size+12, y+size+15,
                                fill="#302c24", outline="")
        element = elemental_type(card)
        if card.startswith("Хоббихорсер"):
            self.canvas.create_line(x-size*.05, y+size*.05,
                                    x-size*.02, y+size*1.35,
                                    fill="#805b3d", width=7)
            self.canvas.create_polygon(x-size*.55, y-size*.25,
                                       x-size*.5, y+size*.85,
                                       x+size*.55, y+size*.85,
                                       x+size*.35, y-size*.3,
                                       fill=data["color"], outline=rarity_color, width=3)
            self.canvas.create_oval(x-size*.36, y-size*1.2,
                                    x+size*.2, y-size*.62,
                                    fill=skin, outline=rarity_color, width=2)
            self.canvas.create_oval(x-size*.4, y-size*1.35,
                                    x+size*.24, y-size*.98,
                                    fill=accent, outline=rarity_color, width=2)
            self.canvas.create_line(x-size*.38, y-size*1.05,
                                    x+size*.22, y-size*1.05,
                                    fill="#eadbb2", width=2)
            self.canvas.create_oval(x+size*.25, y-size*.55,
                                    x+size*1.12, y+size*.02,
                                    fill="#d3b88a", outline="#594638", width=3)
            self.canvas.create_polygon(x+size*.48, y-size*.48,
                                       x+size*.6, y-size*1.03,
                                       x+size*.73, y-size*.48,
                                       x+size*.9, y-size*.92,
                                       x+size*.98, y-size*.23,
                                       fill="#594239", outline="#382f2a")
            self.canvas.create_oval(x+size*.72, y-size*.43,
                                    x+size*.82, y-size*.33,
                                    fill="#211f1d", outline="")
            self.canvas.create_line(x+size*.55, y-size*.15,
                                    x+size*.98, y-size*.08,
                                    fill="#603e31", width=3)
            self.canvas.create_oval(x-size*.16, y-size*.98,
                                    x-size*.08, y-size*.88,
                                    fill="#29231f", outline="")
            self.canvas.create_oval(x+size*.02, y-size*.98,
                                    x+size*.1, y-size*.88,
                                    fill="#29231f", outline="")
            self.canvas.create_arc(x-size*.17, y-size*.86,
                                   x+size*.12, y-size*.7,
                                   start=190, extent=160, style="arc",
                                   outline="#754c43", width=2)
        elif card.startswith("Фурри") or card.startswith("Кот-батон") or "кот" in card.lower():
            self.canvas.create_polygon(x-size*.55, y-size*.1,
                                       x-size*.38, y+size*.82,
                                       x+size*.38, y+size*.82,
                                       x+size*.55, y-size*.1,
                                       fill=data["color"], outline=rarity_color, width=3)
            self.canvas.create_polygon(x-size*.43, y-size*.72,
                                       x-size*.72, y-size*1.55,
                                       x-size*.08, y-size*.98,
                                       x+size*.08, y-size*.98,
                                       x+size*.72, y-size*1.55,
                                       x+size*.43, y-size*.72,
                                       fill=data["color"], outline=rarity_color, width=2)
            self.canvas.create_oval(x-size*.55, y-size*1.2,
                                    x+size*.55, y-size*.1,
                                    fill="#dfc79d", outline=rarity_color, width=2)
            self.canvas.create_polygon(x-size*.28, y-size*.1,
                                       x+size*.28, y-size*.1,
                                       x, y+size*.2,
                                       fill="#f0d7c9", outline="#594638")
            for eye_x in (-size*.2, size*.2):
                eye_height = .16 if face_style in (1, 4) else .19
                self.canvas.create_oval(x+eye_x-size*.055, y-size*.68,
                                        x+eye_x+size*.055, y-size*.68+size*eye_height,
                                        fill="#24201e", outline="")
                self.canvas.create_line(x+eye_x-size*.08, y-size*.73,
                                        x+eye_x+size*.08, y-size*.76,
                                        fill="#594638", width=2)
            self.canvas.create_polygon(x-size*.07, y-size*.08,
                                       x+size*.07, y-size*.08,
                                       x, y+size*.02,
                                       fill="#d67883", outline="")
            self.canvas.create_arc(x-size*.1, y-size*.1,
                                   x+size*.1, y+size*.16,
                                   start=205 if face_style % 2 else 15,
                                   extent=140, style="arc",
                                   outline="#754c43", width=2)
            if face_style in (2, 5):
                self.canvas.create_oval(x-size*.36, y-size*.22,
                                        x-size*.29, y-size*.15,
                                        fill=accent, outline="")
                self.canvas.create_oval(x+size*.29, y-size*.22,
                                        x+size*.36, y-size*.15,
                                        fill=accent, outline="")
            self.canvas.create_arc(x+size*.28, y-size*.05,
                                   x+size*1.1, y+size*.75,
                                   start=100, extent=250, style="arc",
                                   outline=data["color"], width=5)
        elif element == "fire":
            self.canvas.create_polygon(x-size*.8, y+size*.8,
                                       x-size*.65, y-size*.1,
                                       x-size*.3, y-size*.55,
                                       x-size*.12, y-size*1.5,
                                       x+size*.28, y-size*.75,
                                       x+size*.52, y-size*1.2,
                                       x+size*.82, y-size*.25,
                                       x+size*.65, y+size*.8,
                                       fill="#d94f32", outline="#ffbe55", width=3)
            self.canvas.create_polygon(x-size*.38, y+size*.58,
                                       x-size*.18, y-size*.18,
                                       x+size*.05, y-size*.62,
                                       x+size*.3, y-size*.15,
                                       x+size*.4, y+size*.58,
                                       fill="#ffb43f", outline="#ffe58a", width=2)
            self.canvas.create_oval(x-size*.12, y+size*.05,
                                    x+size*.12, y+size*.28,
                                    fill="#fff1b1", outline="")
        elif element == "ice":
            self.canvas.create_polygon(x, y-size*1.25,
                                       x+size*.8, y-size*.45,
                                       x+size*.62, y+size*.62,
                                       x, y+size,
                                       x-size*.62, y+size*.62,
                                       x-size*.8, y-size*.45,
                                       fill="#73bedb", outline="#e5fbff", width=3)
            self.canvas.create_polygon(x-size*.18, y-size*.15,
                                       x-size*.6, y-size*.85,
                                       x-size*.28, y-size*.72,
                                       x, y-size*1.18,
                                       x+size*.25, y-size*.7,
                                       x+size*.62, y-size*.9,
                                       x+size*.28, y-size*.12,
                                       fill="#b9efff", outline="#f2ffff", width=2)
            for eye_x in (-size*.18, size*.18):
                self.canvas.create_oval(x+eye_x-size*.05, y-size*.1,
                                        x+eye_x+size*.05, y+size*.04,
                                        fill="#264f70", outline="")
        elif element == "lightning":
            self.canvas.create_polygon(x+size*.12, y-size*1.35,
                                       x-size*.48, y-size*.22,
                                       x-size*.06, y-size*.22,
                                       x-size*.28, y+size*.95,
                                       x+size*.55, y-size*.18,
                                       x+size*.12, y-size*.18,
                                       x+size*.42, y-size*1.35,
                                       fill="#5b9fe6", outline="#e5fbff", width=3)
            self.canvas.create_line(x-size*.78, y-size*.62,
                                    x-size*.46, y-size*.45,
                                    x-size*.66, y-size*.2,
                                    fill="#b6edff", width=4)
            self.canvas.create_line(x+size*.62, y+size*.25,
                                    x+size*.38, y+size*.42,
                                    x+size*.72, y+size*.7,
                                    fill="#b6edff", width=4)
        elif element == "water":
            self.canvas.create_oval(x-size*.65, y-size*.95,
                                    x+size*.65, y+size*.05,
                                    fill="#567fc4", outline="#b9e8ff", width=3)
            self.canvas.create_oval(x-size*.35, y-size*.66,
                                    x+size*.35, y-size*.08,
                                    fill="#80c9e8", outline="#e6faff", width=2)
            for tentacle in (-1, 0, 1):
                start_x = x + tentacle * size*.35
                self.canvas.create_line(start_x, y-size*.05,
                                        start_x+tentacle*size*.35, y+size*.52,
                                        start_x+tentacle*size*.18, y+size,
                                        fill="#6574c8", width=7, smooth=True)
            self.canvas.create_oval(x-size*.1, y-size*.48,
                                    x-size*.02, y-size*.37,
                                    fill="#fff3c1", outline="")
            self.canvas.create_oval(x+size*.02, y-size*.48,
                                    x+size*.1, y-size*.37,
                                    fill="#fff3c1", outline="")
        else:
            body_style = model % 6
            if body_style == 0:
                self.canvas.create_polygon(x-size*.68, y-size*.05,
                                           x-size*.48, y+size*.8,
                                           x, y+size,
                                           x+size*.48, y+size*.8,
                                           x+size*.68, y-size*.05,
                                           fill=data["color"], outline=rarity_color, width=3)
            elif body_style == 1:
                self.canvas.create_oval(x-size*.7, y-size*.12,
                                        x+size*.7, y+size*.9,
                                        fill=data["color"], outline=rarity_color, width=3)
            elif body_style == 2:
                self.canvas.create_rectangle(x-size*.62, y-size*.05,
                                             x+size*.62, y+size*.92,
                                             fill=data["color"], outline=rarity_color, width=3)
            elif body_style == 3:
                self.canvas.create_polygon(x-size*.8, y+size*.05,
                                           x-size*.45, y-size*.2,
                                           x+size*.45, y-size*.2,
                                           x+size*.8, y+size*.05,
                                           x+size*.5, y+size*.9,
                                           x-size*.5, y+size*.9,
                                           fill=data["color"], outline=rarity_color, width=3)
            elif body_style == 4:
                self.canvas.create_polygon(x-size*.55, y-size*.15,
                                           x+size*.55, y-size*.15,
                                           x+size*.72, y+size*.22,
                                           x+size*.38, y+size*.98,
                                           x-size*.38, y+size*.98,
                                           x-size*.72, y+size*.22,
                                           fill=data["color"], outline=rarity_color, width=3)
            else:
                self.canvas.create_polygon(x-size*.76, y+size*.02,
                                           x-size*.3, y-size*.2,
                                           x+size*.3, y-size*.2,
                                           x+size*.76, y+size*.02,
                                           x+size*.36, y+size*.95,
                                           x-size*.36, y+size*.95,
                                           fill=data["color"], outline=rarity_color, width=3)

            face_x, face_y = x, y-size*.76
            self.canvas.create_oval(face_x-size*.47, face_y-size*.52,
                                    face_x+size*.47, face_y+size*.52,
                                    fill=skin, outline=rarity_color, width=2)
            if head_style == 0:
                self.canvas.create_polygon(x-size*.43, face_y-size*.35,
                                           x-size*.24, face_y-size*.95,
                                           x+size*.06, face_y-size*.52,
                                           x+size*.36, face_y-size*.93,
                                           x+size*.43, face_y-size*.32,
                                           fill=accent, outline="#514638", width=2)
            elif head_style == 1:
                for side in (-1, 1):
                    self.canvas.create_polygon(x+side*size*.3, face_y-size*.25,
                                               x+side*size*.62, face_y-size*.93,
                                               x+side*size*.12, face_y-size*.48,
                                               fill=accent, outline="#514638", width=2)
            elif head_style == 2:
                self.canvas.create_oval(x-size*.52, face_y-size*.72,
                                        x+size*.52, face_y-size*.2,
                                        fill=accent, outline="#514638", width=2)
                self.canvas.create_line(x-size*.5, face_y-size*.2,
                                        x+size*.5, face_y-size*.2,
                                        fill="#eadbb2", width=2)
            elif head_style == 3:
                self.canvas.create_polygon(x-size*.48, face_y-size*.24,
                                           x-size*.4, face_y-size*.75,
                                           x-size*.12, face_y-size*.48,
                                           x+size*.08, face_y-size*.88,
                                           x+size*.22, face_y-size*.47,
                                           x+size*.48, face_y-size*.72,
                                           x+size*.48, face_y-size*.2,
                                           fill=accent, outline="#514638", width=2)
            elif head_style == 4:
                self.canvas.create_line(x-size*.44, face_y-size*.18,
                                        x+size*.44, face_y-size*.18,
                                        fill=accent, width=4)
                self.canvas.create_oval(x-size*.09, face_y-size*.32,
                                        x+size*.09, face_y-size*.08,
                                        fill="#f2d879", outline="#514638")
            else:
                self.canvas.create_oval(x-size*.54, face_y-size*.5,
                                        x+size*.54, face_y-size*.16,
                                        fill=accent, outline="#514638", width=2)

            eye_y = face_y-size*.02
            if face_style == 0:
                for eye_x in (-.2, .2):
                    self.canvas.create_oval(x+size*(eye_x-.07), eye_y-size*.09,
                                            x+size*(eye_x+.07), eye_y+size*.1,
                                            fill="#fff4d6", outline="#342e28")
                    self.canvas.create_oval(x+size*(eye_x-.025), eye_y-size*.04,
                                            x+size*(eye_x+.04), eye_y+size*.07,
                                            fill="#24201e", outline="")
                self.canvas.create_arc(x-size*.13, face_y+size*.13,
                                       x+size*.13, face_y+size*.32,
                                       start=190, extent=160, style="arc",
                                       outline="#754c43", width=2)
            elif face_style == 1:
                self.canvas.create_line(x-size*.31, eye_y,
                                        x-size*.08, eye_y-size*.04,
                                        fill="#342e28", width=4)
                self.canvas.create_line(x+size*.08, eye_y-size*.04,
                                        x+size*.31, eye_y,
                                        fill="#342e28", width=4)
                self.canvas.create_line(x-size*.12, face_y+size*.22,
                                        x+size*.12, face_y+size*.22,
                                        fill="#754c43", width=2)
            elif face_style == 2:
                for eye_x in (-.2, .2):
                    self.canvas.create_oval(x+size*(eye_x-.075), eye_y-size*.08,
                                            x+size*(eye_x+.075), eye_y+size*.08,
                                            outline="#342e28", width=2)
                self.canvas.create_line(x-size*.3, eye_y-size*.16,
                                        x+size*.3, eye_y-size*.16,
                                        fill=accent, width=3)
            elif face_style == 3:
                self.canvas.create_rectangle(x-size*.36, eye_y-size*.08,
                                             x+size*.36, eye_y+size*.12,
                                             fill="#55443d", outline=accent, width=2)
                self.canvas.create_line(x-size*.12, face_y+size*.25,
                                        x+size*.12, face_y+size*.25,
                                        fill="#d9c9ad", width=2)
            elif face_style == 4:
                for eye_x in (-.2, .2):
                    self.canvas.create_oval(x+size*(eye_x-.06), eye_y-size*.07,
                                            x+size*(eye_x+.06), eye_y+size*.07,
                                            fill="#24201e", outline="")
                self.canvas.create_line(x-size*.08, face_y+size*.18,
                                        x+size*.22, face_y+size*.22,
                                        fill="#754c43", width=2)
                self.canvas.create_line(x-size*.37, face_y-size*.02,
                                        x-size*.05, face_y+size*.12,
                                        fill=accent, width=2)
            else:
                self.canvas.create_oval(x-size*.28, eye_y-size*.08,
                                        x-size*.08, eye_y+size*.09,
                                        fill="#24201e", outline="")
                self.canvas.create_line(x+size*.08, eye_y,
                                        x+size*.3, eye_y,
                                        fill="#342e28", width=3)
                self.canvas.create_line(x-size*.12, face_y+size*.24,
                                        x+size*.13, face_y+size*.18,
                                        fill="#754c43", width=2)

        if not data.get("spell") and not data.get("flying"):
            self.draw_character_texture(card, data, x, y+size*.35, size)
            is_horse = card.startswith("Хоббихорсер")
            is_furry = (card.startswith("Фурри") or card.startswith("Кот-батон")
                        or "кот" in card.lower())
            if element != "water" and not data.get("flying"):
                self.draw_profile_weapon(
                    x, y, size, accent, -1 if is_horse or is_furry else 1,
                    (seed + model*5) % 5, data["range"] > 55,
                )

        self.canvas.create_text(210, 160, text=card,
                                fill="#fff1c4", font=("TkDefaultFont", 16, "bold"))
        self.canvas.create_text(210, 185,
                                text=f"{data['rarity']} • УРОВЕНЬ {level}",
                                fill=rarity_color, font=("TkDefaultFont", 10, "bold"))
        hp = round(data["hp"] * (1 + 0.08 * (level - 1)))
        damage = round(data["damage"] * (1 + 0.07 * (level - 1)))
        self.canvas.create_text(210, 405,
                                text=f"HP {hp}  •  Урон {damage}  •  Скорость {data['speed']}",
                                fill="#dbe5cf", font=("TkDefaultFont", 9, "bold"))

    def show_card_profile(self, card):
        if card not in self.unlocked_cards:
            return
        self.running = False
        self.paused = False
        self.profile_card = card
        self.screen = "card_profile"
        data = CARDS[card]
        level = self.card_levels.get(card, 1)
        arena = ARENAS[self.arena_index]
        self.canvas.configure(bg=arena[1])
        self.clear_canvas()
        horror_level = 0 if self.arena_index < 5 else max(1, min(4, (self.arena_index - 5) // 10 + 1))
        profile_fill = "#2c322d" if horror_level == 0 else "#30272a"
        profile_outline = (data.get("rarity_color", "#d8c58a")
                           if horror_level == 0 else "#9d4545")
        self.canvas.create_rectangle(60, 70, 900, 500, fill=profile_fill,
                                     outline=profile_outline, width=4)
        if horror_level > 0:
            blood_color = "#7f3030" if horror_level < 3 else "#aa3935"
            for crack_index in range(horror_level + 1):
                y = 120 + crack_index * 68
                self.canvas.create_line(75, y, 230, y+25,
                                        fill=blood_color, width=2)
                self.canvas.create_line(420, y+20, 885, y,
                                        fill=blood_color, width=1)
            if horror_level >= 2:
                self.canvas.create_text(380, 110, text="☠",
                                        fill="#d2c8ac", font=("TkDefaultFont", 42, "bold"))
        self.canvas.create_text(480, 105, text=card,
                                fill="#fff1c4", font=("TkDefaultFont", 26, "bold"))
        self.draw_character_profile(card, level)
        hp = round(data["hp"] * (1 + 0.08 * (level - 1)))
        damage = round(data["damage"] * (1 + 0.07 * (level - 1)))
        self.canvas.create_text(510, 210, anchor="w",
                                text=f"РЕДКОСТЬ: {data['rarity']}\nУРОВЕНЬ: {level}\nHP: {hp}\nУРОН: {damage}\nСКОРОСТЬ: {data['speed']}\nДАЛЬНОСТЬ: {data['range']}",
                                fill="#e5e1c7", font=("TkDefaultFont", 12, "bold"),
                                justify="left")
        self.canvas.create_text(510, 370, anchor="w", width=330,
                                text="ИСТОРИЯ\n" + self.card_story(card),
                                fill="#d5cba8", font=("TkDefaultFont", 9),
                                justify="left")
        self.button(340, 430, 620, 485, "НАЗАД В КОЛЛЕКЦИЮ",
                    "#b9d8ca", "#342c23", self.show_collection)
        self.apply_canvas_scale()

    def select_upgrade_card(self, card):
        self.upgrade_card = card
        self.collection_page = list(CARDS).index(card) // 20
        self.show_collection()

    def change_collection_page(self, delta):
        page_count = max(1, (len(CARDS) + 19) // 20)
        self.collection_page = max(0, min(page_count - 1, self.collection_page + delta))
        self.show_collection()

    def upgrade_selected_card(self):
        card = self.upgrade_card
        if card not in self.unlocked_cards:
            self.notice = "Сначала найди карту в сундуке или купи её за золото."
        else:
            level = self.card_levels[card]
            gold_cost = card_upgrade_cost(card, level)
            if level >= 5:
                self.notice = "У карты уже максимальный уровень."
            elif self.gold < gold_cost:
                self.notice = f"Нужно {gold_cost} золота."
            else:
                self.gold -= gold_cost
                self.card_levels[card] += 1
                self.upgrades_done += 1
                self.notice = f"«{card}» улучшена до уровня {self.card_levels[card]}!"
                self.save()
        self.show_collection()
        if self.notice:
            self.canvas.create_text(480*self.canvas_scale_x,
                                    540*self.canvas_scale_y,
                                    text=self.notice, fill="#8ff0a4",
                                    font=("TkDefaultFont", 9, "bold"))

    def buy_selected_card(self):
        card = self.upgrade_card
        if card not in CARDS:
            self.notice = "Сначала выбери карту."
        elif card in self.unlocked_cards:
            self.notice = f"Карта «{card}» уже открыта."
        else:
            unlock_cost = card_unlock_cost(card)
            if self.gold < unlock_cost:
                self.notice = f"Нужно {unlock_cost} золота."
            else:
                self.gold -= unlock_cost
                self.unlocked_cards.append(card)
                self.notice = f"Карта «{card}» ({CARDS[card]['rarity']}) куплена за {unlock_cost} золота!"
                self.save()
        self.show_collection()
        if self.notice:
            self.canvas.create_text(480*self.canvas_scale_x,
                                    540*self.canvas_scale_y,
                                    text=self.notice, fill="#8ff0a4",
                                    font=("TkDefaultFont", 9, "bold"))

    def show_achievements(self):
        self.running = False
        self.paused = False
        self.loop_token += 1
        self.screen = "achievements"
        self.canvas.configure(bg="#30352e")
        self.clear_canvas()
        self.canvas.create_text(480, 48, text="КУБКИ И СТРАННЫЕ ЦЕЛИ",
                                fill="#fff1c4", font=("TkDefaultFont", 27, "bold"))
        self.canvas.create_text(480, 87, text=f"У тебя {self.trophies} кубков. Куда их складывать — неизвестно.",
                                fill="#e5d7a8", font=("TkDefaultFont", 11))
        achievements = [
            ("Первый блин не сгорел", self.battles_played, 1, "сыграй бой"),
            ("Архитектурный критик", self.crowns_earned, 10, "снеси 10 башен"),
            ("Карточный шкаф", len(self.unlocked_cards), len(CARDS), "открой все карты"),
            ("Карточный мастеровер", self.upgrades_done, 1, "улучши карту"),
            ("Кубковый пылесос", self.trophies, 500, "набери кубки"),
        ]
        for index, (title, progress, goal, description) in enumerate(achievements):
            y = 130 + index * 75
            complete = progress >= goal
            self.canvas.create_rectangle(135, y, 825, y+60,
                                         fill="#3c4437" if complete else "#292d29",
                                         outline="#d6bd79" if complete else "#62675d", width=2)
            self.canvas.create_text(160, y+18, anchor="w",
                                    text=("✓ " if complete else "○ ") + title,
                                    fill="#f2d579" if complete else "#e2dfce",
                                    font=("TkDefaultFont", 12, "bold"))
            self.canvas.create_text(160, y+42, anchor="w", text=description,
                                    fill="#bbb7a3", font=("TkDefaultFont", 9))
            self.canvas.create_text(800, y+30, anchor="e",
                                    text=f"{min(progress, goal)}/{goal}",
                                    fill="#fff1c4", font=("TkDefaultFont", 11, "bold"))
        self.button(180, 500, 420, 540, "БОЕВОЙ ПРОПУСК", "#e7c56d", "#342c23",
                    self.show_battle_pass)
        self.button(540, 500, 780, 540, "АРЕНА И ОБЛИКИ", "#c5d5e0", "#342c23",
                    self.show_appearance)
        self.bottom_nav("achievements")
        self.apply_canvas_scale()

    def show_battle_pass(self):
        self.running = False
        self.paused = False
        self.loop_token += 1
        self.screen = "battle_pass"
        arena = ARENAS[self.arena_index]
        self.canvas.configure(bg=arena[1])
        self.clear_canvas()
        tier = self.battle_pass_xp // 100 + 1
        progress = self.battle_pass_xp % 100
        self.canvas.create_text(480, 60, text="БОЕВОЙ ПРОПУСК",
                                fill="#fff1c4", font=("TkDefaultFont", 30, "bold"))
        self.canvas.create_text(480, 101, text="ИГРАЙ БОИ, ПОЛУЧАЙ ОПЫТ И ЗАБИРАЙ НАГРАДЫ",
                                fill=arena[3], font=("TkDefaultFont", 11, "bold"))
        self.canvas.create_rectangle(200, 150, 760, 330, fill="#29352d",
                                     outline="#d8b36a", width=4)
        self.canvas.create_text(480, 190, text=f"УРОВЕНЬ ПРОПУСКА  {tier}",
                                fill="#f3d9a1", font=("TkDefaultFont", 23, "bold"))
        self.canvas.create_text(480, 231, text=f"ОПЫТ  {progress}/100",
                                fill="#e9e2c5", font=("TkDefaultFont", 13, "bold"))
        self.canvas.create_rectangle(280, 253, 680, 276, fill="#423b34",
                                     outline="#d6c6a0", width=2)
        if progress:
            self.canvas.create_rectangle(283, 256, 283+394*progress/100, 273,
                                         fill="#cf58bd", outline="")
        next_tier = tier + 1
        reward = "50 монет"
        if next_tier % 3 == 0:
            reward += " и сундук"
        self.canvas.create_text(480, 301, text=f"СЛЕДУЮЩИЙ УРОВЕНЬ: {reward}",
                                fill="#f3d37a", font=("TkDefaultFont", 11, "bold"))
        self.canvas.create_text(480, 376, text=f"МОНЕТЫ: {self.gold}     •     СУНДУКИ: {self.chests}",
                                fill="#fff1c4", font=("TkDefaultFont", 14, "bold"))
        self.canvas.create_text(480, 414,
                                text="За бой: 25 XP + 15 XP за каждую корону + 25 XP за победу.",
                                fill="#e9e2c5", font=("TkDefaultFont", 10))
        self.canvas.create_text(480, 440,
                                text="Каждый уровень приносит 50 монет; каждый 3-й — ещё и сундук.",
                                fill="#e9e2c5", font=("TkDefaultFont", 10))
        self.button(350, 510, 610, 560, "НАЗАД В КРЕПОСТЬ", "#f0ca6c", "#342c23",
                    self.show_menu)
        self.apply_canvas_scale()

    def draw_chest(self, x, y, opened):
        if opened:
            self.canvas.create_arc(x-90, y-35, x+90, y+50, start=0, extent=180,
                                   fill="#b77532", outline="#f2d47b", width=4)
        else:
            self.canvas.create_arc(x-90, y-65, x+90, y+25, start=0, extent=180,
                                   fill="#a8662d", outline="#f2d47b", width=4)
        self.canvas.create_rectangle(x-90, y-20, x+90, y+60,
                                     fill="#8f552e", outline="#f2d47b", width=4)
        self.canvas.create_rectangle(x-72, y-5, x+72, y+14,
                                     fill="#d2a24b", outline="#f8df98", width=2)
        self.canvas.create_rectangle(x-13, y-12, x+13, y+25,
                                     fill="#edce76", outline="#78532b", width=2)
        self.canvas.create_oval(x-5, y+1, x+5, y+11,
                                fill="#624323", outline="")

    def open_chest(self):
        if self.chests < 1:
            self.last_reward = "Сундуков нет. Победи в бою или купи сундук за золото."
            self.show_chests()
            return
        self.chests -= 1
        self.chest_revealed = True
        gold_reward = random.randint(60, 120)
        self.gold += gold_reward
        locked_cards = [name for name in CARDS if name not in self.unlocked_cards]
        if locked_cards and random.random() < 0.65:
            card = random.choice(locked_cards)
            self.unlocked_cards.append(card)
            reward = f"+{gold_reward} золота, открыта карта «{card}»"
        else:
            card = random.choice(self.unlocked_cards)
            duplicate_reward = 40
            self.gold += duplicate_reward
            reward = f"+{gold_reward} золота, повтор карты «{card}»: +{duplicate_reward} золота"
        self.last_reward = reward
        self.save()
        self.show_chests()
        self.canvas.create_text(480*self.canvas_scale_x,
                                515*self.canvas_scale_y,
                                text=f"НАГРАДА: {reward}",
                                fill="#8ff0a4", font=("TkDefaultFont", 10, "bold"))

    def buy_chest(self):
        if self.gold < 100:
            self.last_reward = "Не хватает золота: нужно 100."
        else:
            self.gold -= 100
            self.chests += 1
            self.chest_revealed = False
            self.last_reward = "Сундук куплен! Теперь его можно открыть."
        self.save()
        self.show_chests()

    def button(self, x1, y1, x2, y2, text, color, text_color, command,
               outline=None, width=2):
        outline = outline or color
        rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#31372d",
                                            outline=outline, width=width)
        label = self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text=text,
                                        fill=color, font=("TkDefaultFont", 11, "bold"))

        def invoke(event):
            command()
            return "break"

        for item in (rect, label):
            self.canvas.tag_bind(item, "<Button-1>", invoke)
            self.canvas.tag_bind(item, "<Enter>",
                                 lambda event, shape=rect: self.canvas.itemconfigure(shape, fill="#485141"))
            self.canvas.tag_bind(item, "<Leave>",
                                 lambda event, shape=rect: self.canvas.itemconfigure(shape, fill="#31372d"))

    def select_skin(self, index):
        self.skin_index = index
        self.save()
        self.show_appearance()

    def toggle_mode(self):
        modes = ("sudden", "classic", "meme", "furry_horse")
        self.mode = modes[(modes.index(self.mode) + 1) % len(modes)]
        if self.screen == "appearance":
            self.show_appearance()
        else:
            self.show_menu()

    def mode_label(self):
        return {
            "sudden": "БЫСТРЫЙ",
            "classic": "КЛАССИКА",
            "meme": "67 ВОЙНЫ",
            "furry_horse": "ФУРРИ против ХОББИХОРСЕРОВ",
        }.get(self.mode, "БЫСТРЫЙ")

    def select_match_mode(self, mode):
        self.mode = mode
        self.show_match_setup()

    def show_match_setup(self):
        self.running = False
        self.paused = False
        self.loop_token += 1
        self.screen = "match_setup"
        arena = ARENAS[self.arena_index]
        self.canvas.configure(bg=arena[1])
        self.clear_canvas()
        self.canvas.create_text(480, 55, text="ПОДГОТОВКА К БОЮ",
                                fill="#fff1c4", font=("TkDefaultFont", 28, "bold"))
        self.canvas.create_text(480, 92,
                                text=f"КОЛОДА: {len(self.battle_deck)}/8  •  АРЕНА: {arena[0]}",
                                fill=arena[3], font=("TkDefaultFont", 11, "bold"))

        modes = (
            ("sudden", "БЫСТРЫЙ", "2 минуты  •  эликсир x2 в последнюю минуту"),
            ("classic", "КЛАССИКА", "3 минуты  •  обычный темп с овертаймом"),
            ("meme", "67 ВОЙНЫ", "67 секунд  •  эликсир x3  •  абсолютно случайные мем-карты"),
            ("furry_horse", "ФУРРИ против ХОББИХОРСЕРОВ", "Выбери сторону  •  уникальные фракционные колоды"),
        )
        for index, (mode, title, description) in enumerate(modes):
            y = 112 + index * 67
            selected = mode == self.mode
            fill = "#efe0a4" if selected else "#d1d5c6"
            self.button(220, y, 740, y+58, title, fill, "#342c23",
                        lambda mode=mode: self.select_match_mode(mode),
                        outline="#f0ca6c" if selected else "#777d70", width=3 if selected else 2)
            self.canvas.create_text(480, y+42, text=description,
                                    fill="#5b5547", font=("TkDefaultFont", 8))

        if self.mode == "furry_horse":
            furry_selected = self.furry_vs_horse_side == "furry"
            horse_selected = self.furry_vs_horse_side == "horse"
            self.button(220, 405, 460, 465, "ИГРАТЬ ЗА ФУРРИ",
                        "#d9a2bc" if furry_selected else "#cfd0c5", "#342c23",
                        lambda: self.select_furry_horse_side("furry"),
                        outline="#f2b4d0" if furry_selected else "#777d70", width=3 if furry_selected else 2)
            self.button(500, 405, 740, 465, "ИГРАТЬ ЗА ХОББИХОРСЕРОВ",
                        "#b9a276" if horse_selected else "#cfd0c5", "#342c23",
                        lambda: self.select_furry_horse_side("horse"),
                        outline="#d7c18a" if horse_selected else "#777d70", width=3 if horse_selected else 2)
            ready_y = 478
        else:
            ready_y = 455
        self.button(330, ready_y, 630, ready_y+60, "ГОТОВО", "#f0ca6c", "#342c23",
                    self.start_game, outline="#fff0a8", width=3)
        self.button(330, 552, 630, 594, "НАЗАД", "#b8a1b3", "#342c23",
                    self.show_menu)
        self.apply_canvas_scale()

    def select_furry_horse_side(self, side):
        self.furry_vs_horse_side = side
        self.show_match_setup()

    def track_mouse(self, event):
        self.mouse_x, self.mouse_y = self.design_point(event.x, event.y)

    def deployment_zone_contains(self, side, x, y, lane):
        expanded_lanes = (self.player_expanded_lanes if side == "player"
                          else self.bot_expanded_lanes)
        expanded = lane in expanded_lanes
        if not (135 <= x <= 825):
            return False
        if expanded:
            lane_bounds = (135 <= x <= 470 if lane == 0 else 490 <= x <= 825)
            if not lane_bounds:
                return False
            y_bounds = (255 <= y <= 515 if side == "player"
                        else 84 <= y <= 342)
        else:
            y_bounds = (350 <= y <= 515 if side == "player"
                        else 115 <= y <= 245)
        if not y_bounds:
            return False
        return not (258 <= y <= 342 and abs(x - BRIDGES[lane]) > 34)

    def bot_spawn_position(self, lane, data):
        expanded = lane in self.bot_expanded_lanes
        spread = math.ceil(max(
            (abs((index - (data["count"] - 1) / 2) * 20)
             for index in range(data["count"])),
            default=0,
        ))
        margin = data["size"] + spread + 2
        x_min, x_max = ((135 + margin, 470 - margin) if lane == 0
                        else (490 + margin, 825 - margin))
        if x_min > x_max:
            return None
        y_min, y_max = (84, 342) if expanded else (115, 245)
        for _ in range(64):
            x = random.randint(x_min, x_max)
            y = random.randint(y_min, y_max)
            if not self.deployment_zone_contains("bot", x, y, lane):
                continue
            blocked = any(
                tower.hp > 0
                and math.hypot(tower.x - x, tower.y - y)
                < tower.radius + data["size"] + 5
                for tower in self.towers
            )
            if not blocked:
                return x, y
        return None

    def start_game(self):
        arena = ARENAS[self.arena_index]
        self.bot_name = random.choice(BOT_NAMES)
        self.bot_level = 1 if self.mode == "furry_horse" else random.randint(1, 5)
        meme_cards = [
            name for name in CARDS
            if not CARDS[name].get("spell")
            and (name.startswith(tuple(MEME_CARD_PREFIXES))
                 or name in ("67-Мем-стример", "Кринж-кот", "Сигма-кракен"))
        ]
        paired_bot_deck = None
        paired_bot_levels = None
        if self.mode == "furry_horse":
            furry_cards = [name for name in CARDS
                           if (name.startswith("Фурри") or name.startswith("Кот-батон"))
                           and name not in ("Фурри-фейерверк",)
                           and not CARDS[name].get("spell")]
            horse_cards = [name for name in CARDS
                           if name.startswith("Хоббихорсер")
                           and name not in ("Хоббихорсерский таран",)
                           and not CARDS[name].get("spell")]
            if len(furry_cards) < 8 or len(horse_cards) < 8:
                furry_cards = ["Фурри на самокате", "Фурри техномаг", "Фурри берсерк",
                               "Фурри сапёр", "Фурри защитник дивана", "Фурри пицца-рейдер",
                               "Фурри повелитель носков", "Фурри звёздный стажёр"]
                horse_cards = ["Хоббихорсер на самокате", "Хоббихорсер техномаг",
                               "Хоббихорсер берсерк", "Хоббихорсер сапёр",
                               "Хоббихорсер защитник дивана", "Хоббихорсер пицца-рейдер",
                               "Хоббихорсер повелитель носков", "Хоббихорсер звёздный стажёр"]
            furry_cards = [name for name in furry_cards if name in CARDS]
            horse_cards = [name for name in horse_cards if name in CARDS]
            furry_by_role = {
                name.removeprefix("Фурри "): name
                for name in furry_cards if name.startswith("Фурри ")
            }
            horse_by_role = {
                name.removeprefix("Хоббихорсер "): name
                for name in horse_cards if name.startswith("Хоббихорсер ")
            }
            matching_roles = sorted(furry_by_role.keys() & horse_by_role.keys())
            selected_roles = random.sample(matching_roles, 6)
            furry_units = [furry_by_role[role] for role in selected_roles]
            horse_units = [horse_by_role[role] for role in selected_roles]
            if self.furry_vs_horse_side == "furry":
                player_meme_deck = furry_units + ["Фурри-фейерверк", "Мур-регенерация"]
                paired_bot_deck = horse_units + ["Хоббихорсерский таран", "Копытный гул"]
                paired_bot_levels = {
                    horse_by_role[role]: self.card_levels.get(furry_by_role[role], 1)
                    for role in selected_roles
                }
                paired_bot_levels.update({
                    "Хоббихорсерский таран": self.card_levels.get("Фурри-фейерверк", 1),
                    "Копытный гул": self.card_levels.get("Мур-регенерация", 1),
                })
            else:
                player_meme_deck = horse_units + ["Хоббихорсерский таран", "Копытный гул"]
                paired_bot_deck = furry_units + ["Фурри-фейерверк", "Мур-регенерация"]
                paired_bot_levels = {
                    furry_by_role[role]: self.card_levels.get(horse_by_role[role], 1)
                    for role in selected_roles
                }
                paired_bot_levels.update({
                    "Фурри-фейерверк": self.card_levels.get("Хоббихорсерский таран", 1),
                    "Мур-регенерация": self.card_levels.get("Копытный гул", 1),
                })
            available_cards = paired_bot_deck
        elif self.mode == "meme" and len(meme_cards) >= 8:
            available_cards = meme_cards
            player_meme_deck = random.sample(meme_cards, 8)
        else:
            meme_names = set(meme_cards)
            available_cards = [
                name for name in CARDS
                if not CARDS[name].get("spell") and name not in meme_names
            ]
            player_meme_deck = None
        self.bot_deck = (
            paired_bot_deck[:] if paired_bot_deck is not None else
            balanced_bot_deck(
                available_cards,
                player_meme_deck if player_meme_deck is not None else self.battle_deck,
            )
        )
        self.bot_card_levels = (paired_bot_levels if paired_bot_levels is not None else {
            card: random.randint(max(1, self.bot_level - 1),
                                 min(5, self.bot_level + 1))
            for card in self.bot_deck
        })
        self.canvas.configure(bg=arena[1])
        self.clear_canvas()
        self.running = True
        self.paused = False
        self.screen = "game"
        self.loop_token += 1
        self.selected_card = None
        self.notice = ""
        self.time_left = 67 if self.mode == "meme" else (
            120 if self.mode == "sudden" else 180
        )
        self.player_elixir = STARTING_ELIXIR
        self.bot_elixir = STARTING_ELIXIR
        self.units = []
        self.projectiles = []
        self.effects = []
        self.player_crowns = 0
        self.bot_crowns = 0
        self.player_expanded_lanes = set()
        self.bot_expanded_lanes = set()
        self.overtime = False
        self.overtime_left = 60
        self.overtime_drain_side = None
        self.overtime_drain_tick = 0
        self.forced_winner = None
        self.deck = (player_meme_deck[:] if player_meme_deck is not None
                     else self.battle_deck[:])
        random.shuffle(self.deck)
        self.hand = self.deck[:4]
        self.draw_queue = self.deck[4:]

        self.towers = [
            Tower(250, 505, "player"), Tower(710, 505, "player"),
            Tower(480, 485, "player", True),
            Tower(250, 95, "bot"), Tower(710, 95, "bot"),
            Tower(480, 115, "bot", True),
        ]
        self.last_tick = int(self.root.tk.call("clock", "milliseconds"))
        self.game_loop(self.loop_token)

    def click(self, event):
        if not self.running:
            return
        x, y = self.design_point(event.x, event.y)
        if self.paused:
            if 330 <= x <= 630 and 278 <= y <= 328:
                self.paused = False
            elif 330 <= x <= 630 and 342 <= y <= 392:
                self.show_menu()
            return
        if self.overtime:
            self.selected_card = None
            self.notice = "В овертайме новые войска не выставляются."
            return

        if not self.selected_card:
            if 535 <= y <= 590 and 255 <= x < 255 + 4*120:
                index = int((x - 255) // 120)
                if 0 <= index < len(self.hand):
                    self.selected_card = self.hand[index]
            return

        if y >= 535:
            self.selected_card = None
            return

        card = self.selected_card
        data = CARDS[card]
        inside_field = 130 <= x <= 830 and 70 <= y <= 530
        lane = 0 if x < 480 else 1
        own_deployment = self.deployment_zone_contains("player", x, y, lane)
        spell_target = data.get("spell") and inside_field and not 265 <= y <= 335
        can_place = spell_target if data.get("spell") else own_deployment and 135 <= x <= 825
        if not can_place:
            self.notice = ("Заклинание нельзя бросать в реку." if data.get("spell")
                           else "Войска размещаются только на своей половине арены.")
            self.selected_card = None
            return
        if data["cost"] > self.player_elixir:
            self.notice = f"Не хватает эликсира для карты «{card}»."
            return

        if data.get("spell"):
            self.cast_spell(card, x, y)
        else:
            blocked = any(
                tower.hp > 0
                and math.hypot(tower.x-x, tower.y-y)
                < tower.radius + data["size"] + 5
                for tower in self.towers
            )
            if blocked:
                self.notice = "Слишком близко к башне — выбери свободное место."
                return
            if len(self.units) + data["count"] > MAX_UNITS:
                self.notice = "На поле уже слишком много бойцов. Подожди, пока освободится место."
                return
            lane = 0 if x < 480 else 1
            spawn_x = max(145, min(815, x))
            spawn_min_y = 255 if lane in self.player_expanded_lanes else 355
            spawn_y = max(spawn_min_y, min(515, y))
            for i in range(data["count"]):
                offset = (i - (data["count"]-1)/2) * 22
                level = self.card_levels.get(card, 1)
                self.units.append(Unit(spawn_x + offset, spawn_y, "player", card, lane, level))
                self.on_unit_spawn(self.units[-1])

        self.notice = ""
        self.player_elixir -= data["cost"]
        self.hand.remove(card)
        next_card = self.draw_queue.pop(0)
        self.hand.append(next_card)
        self.draw_queue.append(card)
        self.selected_card = None

    def cast_spell(self, card, x, y):
        data = CARDS[card]
        level = self.card_levels.get(card, 1)
        damage = round(data["damage"] * (1 + 0.07 * (level - 1)))
        if card in ("Огненный шар", "Фурри-фейерверк", "Хоббихорсерский таран"):
            visual_kind = (
                "furry_fireball" if card == "Фурри-фейерверк" else
                "horse_fireball" if card == "Хоббихорсерский таран" else
                "fireball"
            )
            self.launch_spell_projectile(
                visual_kind, x, y, data["range"], damage, data["color"],
            )
            return
        if card == "Мур-регенерация":
            for unit in self.units:
                if (unit.side == "player" and unit.hp > 0
                        and math.hypot(unit.x-x, unit.y-y) <= data["range"] + unit.size):
                    unit.hp = min(unit.max_hp, unit.hp + 180)
            self.effects.append({"x": x, "y": y, "life": 0.6,
                                 "color": data["color"], "radius": data["range"]})
            return
        if card == "Копытный гул":
            for target in self.units:
                if (target.side == "bot" and target.hp > 0
                        and math.hypot(target.x-x, target.y-y) <= data["range"] + target.size):
                    self.damage_target(target, damage)
                    target.slow_timer = max(target.slow_timer, 2.5)
            for tower in self.towers:
                if (tower.side == "bot" and tower.hp > 0
                        and math.hypot(tower.x-x, tower.y-y) <= data["range"] + tower.radius):
                    self.damage_target(tower, damage)
            self.effects.append({"x": x, "y": y, "life": 0.6,
                                 "color": data["color"], "radius": data["range"]})
            return
        if data.get("spell_kind") == "barrel":
            self.launch_spell_projectile(
                "barrel", x, y, data["range"], 0, data["color"],
            )
            return
        if card == "Молния":
            targets = [
                (math.hypot(target.x-x, target.y-y), target)
                for target in self.units + self.towers
                if target.side == "bot" and target.hp > 0
                and math.hypot(target.x-x, target.y-y)
                <= data["range"] + getattr(target, "size", getattr(target, "radius", 0))
            ]
            for _, target in sorted(targets, key=lambda item: item[0])[:3]:
                self.damage_target(target, damage)
        elif card == "Лечение":
            for unit in self.units:
                if (unit.side == "player" and unit.hp > 0
                        and math.hypot(unit.x-x, unit.y-y) <= data["range"] + unit.size):
                    unit.hp = min(unit.max_hp, unit.hp + 160)
        self.effects.append({"x": x, "y": y, "life": 0.55,
                             "color": data["color"], "radius": data["range"]})

    def launch_spell_projectile(self, spell_kind, x, y, radius, damage, color, side="player"):
        self.projectiles.append({
            "x": 480, "y": 505, "tx": x, "ty": y,
            "damage": damage, "target": None,
            "color": color, "side": side,
            "speed": 430, "visual": spell_kind,
            "spell_kind": spell_kind, "radius": radius,
        })

    def resolve_spell_projectile(self, projectile):
        x, y = projectile["tx"], projectile["ty"]
        radius = projectile["radius"]
        if projectile["spell_kind"] in ("fireball", "furry_fireball", "horse_fireball"):
            for target in self.units + self.towers:
                target_size = getattr(target, "size", getattr(target, "radius", 0))
                if (target.side != projectile["side"] and target.hp > 0
                        and math.hypot(target.x-x, target.y-y) <= radius + target_size):
                    self.damage_target(target, projectile["damage"])
        elif projectile["spell_kind"] == "barrel":
            lane = 0 if x < 480 else 1
            stats = CARDS["Гоблины"]
            count = min(stats["count"], MAX_UNITS - len(self.units))
            for index in range(max(0, count)):
                offset = (index - (count-1)/2) * 16
                self.units.append(Unit(
                    x+offset, y, projectile["side"], "Гоблины", lane,
                    self.card_levels.get("Гоблины", 1),
                ))
                self.on_unit_spawn(self.units[-1])
        self.effects.append({
            "x": x, "y": y, "life": 0.55,
            "color": projectile["color"], "radius": radius,
        })

    def enemy_cast_spell(self, x, y):
        targets = [u for u in self.units if u.side == "player"
                   and math.hypot(u.x-x, u.y-y) <= 75]
        for target in targets:
            self.damage_target(target, 160)
        self.effects.append({"x": x, "y": y, "life": 0.55,
                             "color": "#e96a3a", "radius": 75})

    def damage_splash(self, side, x, y, damage, radius, primary=None):
        if radius <= 0:
            return
        targets = self.units + self.towers
        for target in targets:
            if (target is not primary and target.side != side and target.hp > 0
                    and math.hypot(target.x-x, target.y-y) <= radius):
                self.damage_target(target, round(damage * 0.6))

    def damage_target(self, target, damage):
        if (isinstance(target, Tower) and target.crown and target.hp > 0
                and not target.activated):
            target.activated = True
            self.effects.append({"x": target.x, "y": target.y, "life": 0.6,
                                 "color": "#f4d35e", "radius": 50})
        target.hp -= damage

    def on_unit_spawn(self, unit):
        if unit.stats.get("spawn_lightning"):
            enemies = [target for target in self.units + self.towers
                       if target.side != unit.side and target.hp > 0
                       and math.hypot(target.x-unit.x, target.y-unit.y) <= 135]
            enemies.sort(key=lambda target: math.hypot(
                target.x-unit.x, target.y-unit.y
            ))
            for target in enemies[:3]:
                damage = 135 if getattr(target, "max_hp", 0) <= 100 else 45
                self.damage_target(target, damage)
            self.effects.append({"x": unit.x, "y": unit.y, "life": 0.6,
                                 "color": "#8de6ff", "radius": 135})

    def game_loop(self, token):
        if not self.running or token != self.loop_token:
            return
        now = int(self.root.tk.call("clock", "milliseconds"))
        dt = min((now-self.last_tick)/1000.0, 0.034)
        self.last_tick = now
        if not self.paused:
            self.update(dt)
        if not self.running:
            return
        self.draw()
        self.root.after(33, lambda: self.game_loop(token))

    def update(self, dt):
        if not self.overtime:
            self.time_left = max(0, self.time_left - dt)
        elif self.overtime_left > 0:
            self.overtime_left = max(0, self.overtime_left - dt)
            if self.overtime_left <= 0:
                self.units = []
                self.projectiles = []
                self.selected_card = None
                player_hp = sum(max(0, tower.hp) for tower in self.towers
                                if tower.side == "player")
                bot_hp = sum(max(0, tower.hp) for tower in self.towers
                             if tower.side == "bot")
                self.end_game(overtime_tower_winner(set(), player_hp, bot_hp))
                return
        elixir_speed = 3.0 if self.mode == "meme" else (
            2.0 if self.overtime or self.time_left <= 60 else 1.0
        )
        elixir_gain = dt * elixir_speed / 2.8
        self.player_elixir, self.bot_elixir = accrue_battle_elixir(
            self.player_elixir, self.bot_elixir, elixir_gain
        )

        if (not self.overtime and random.random() < dt * 0.24
            and self.bot_elixir >= 2 and len(self.units) < MAX_UNITS):
            affordable = [name for name in self.bot_deck
                          if not CARDS[name].get("spell")
                          and CARDS[name]["cost"] <= self.bot_elixir
                          and len(self.units) + CARDS[name]["count"] <= MAX_UNITS]
            if affordable:
                card = random.choice(affordable)
                data = CARDS[card]
                for lane in random.sample((0, 1), 2):
                    position = self.bot_spawn_position(lane, data)
                    if position:
                        break
                if position:
                    x, y = position
                    for index in range(data["count"]):
                        offset = (index - (data["count"] - 1) / 2) * 20
                        level = self.bot_card_levels.get(card, self.bot_level)
                        self.units.append(Unit(x+offset, y, "bot", card, lane, level))
                        self.on_unit_spawn(self.units[-1])
                    self.bot_elixir -= data["cost"]
        spell_cost_threshold = 3 if self.mode == "furry_horse" else 4
        if (not self.overtime and random.random() < dt * 0.03
            and self.bot_elixir >= spell_cost_threshold):
            player_units = [u for u in self.units if u.side == "player"]
            if player_units:
                target = random.choice(player_units)
                if self.mode == "furry_horse":
                    if self.furry_vs_horse_side == "furry":
                        bot_spells = ("Хоббихорсерский таран", "Копытный гул")
                    else:
                        bot_spells = ("Фурри-фейерверк", "Мур-регенерация")
                    affordable_spells = [
                        spell for spell in bot_spells
                        if CARDS[spell]["cost"] <= self.bot_elixir
                    ]
                    bot_spell = random.choice(affordable_spells)
                    bot_data = CARDS[bot_spell]
                    bot_spell_level = self.bot_card_levels.get(bot_spell, 1)
                    bot_spell_damage = round(
                        bot_data["damage"] * (1 + 0.07 * (bot_spell_level - 1))
                    )
                    if bot_spell in ("Хоббихорсерский таран", "Фурри-фейерверк"):
                        self.launch_spell_projectile(
                            "horse_fireball" if bot_spell == "Хоббихорсерский таран" else "furry_fireball",
                            target.x, target.y, bot_data["range"],
                            bot_spell_damage, bot_data["color"], side="bot",
                        )
                    elif bot_spell == "Копытный гул":
                        for player_unit in player_units:
                            if math.hypot(player_unit.x-target.x, player_unit.y-target.y) <= bot_data["range"] + player_unit.size:
                                self.damage_target(player_unit, bot_spell_damage)
                                player_unit.slow_timer = max(player_unit.slow_timer, 2.5)
                        for tower in self.towers:
                            if (tower.side == "player" and tower.hp > 0
                                    and math.hypot(tower.x-target.x, tower.y-target.y)
                                    <= bot_data["range"] + tower.radius):
                                self.damage_target(tower, bot_spell_damage)
                        self.effects.append({"x": target.x, "y": target.y, "life": 0.6,
                                             "color": bot_data["color"], "radius": bot_data["range"]})
                    elif bot_spell == "Мур-регенерация":
                        bot_units = [u for u in self.units if u.side == "bot" and u.hp > 0]
                        for bot_unit in bot_units:
                            if math.hypot(bot_unit.x-target.x, bot_unit.y-target.y) <= bot_data["range"] + bot_unit.size:
                                bot_unit.hp = min(bot_unit.max_hp, bot_unit.hp + 180)
                        self.effects.append({"x": target.x, "y": target.y, "life": 0.6,
                                             "color": bot_data["color"], "radius": bot_data["range"]})
                else:
                    self.enemy_cast_spell(target.x, target.y)
                self.bot_elixir -= (
                    bot_data["cost"] if self.mode == "furry_horse" else 4
                )

        for unit in self.units[:]:
            if unit.lifetime is not None:
                unit.lifetime -= dt
                if unit.lifetime <= 0:
                    unit.hp = 0
            if unit.hp <= 0:
                horror_level = 0 if self.arena_index < 5 else max(1, min(4, (self.arena_index - 5) // 10 + 1))
                self.effects.append({"x": unit.x, "y": unit.y, "life": 0.35,
                                     "color": unit.color, "radius": 25,
                                     "corpse": horror_level >= 2,
                                     "horror": horror_level})
                self.units.remove(unit)
                if unit.death_spawn:
                    spawn_data = unit.death_spawn
                    for _ in range(spawn_data.get("count", 1)):
                        level = (self.bot_card_levels.get("Гоблины", self.bot_level)
                                 if unit.side == "bot" else
                                 self.card_levels.get("Гоблины", 1))
                        self.units.append(Unit(
                            unit.x, unit.y, unit.side, unit.card, unit.lane,
                            level=level, stats=spawn_data,
                            display_name="Гоблин-сторож",
                        ))
                        self.on_unit_spawn(self.units[-1])
                continue

            unit.slow_timer = max(0, unit.slow_timer - dt)
            unit.attack_phase = max(0, unit.attack_phase - dt)
            unit.walk_phase += dt * unit.speed * 0.16
            if unit.stats.get("ice_aura"):
                for enemy in self.units:
                    if (enemy.side != unit.side and enemy.hp > 0
                            and math.hypot(enemy.x-unit.x, enemy.y-unit.y) <= 78):
                        enemy.slow_timer = max(enemy.slow_timer, 0.4)

            bridge_x = BRIDGES[unit.lane]
            if (not unit.flying and not unit.is_building
                    and abs(unit.x - bridge_x) <= 45):
                if unit.side == "player" and unit.y <= 335:
                    unit.crossed_bridge = True
                elif unit.side == "bot" and unit.y >= 265:
                    unit.crossed_bridge = True
            enemies = [u for u in self.units
                       if u.side != unit.side and u.hp > 0]
            enemy_towers = [t for t in self.towers
                            if t.side != unit.side and t.hp > 0]
            enemy_structures = [u for u in enemies if u.is_building] + enemy_towers
            lane_structures = [
                structure for structure in enemy_structures
                if (getattr(structure, "lane", 0 if structure.x < 480 else 1)
                    == unit.lane)
            ]
            if not lane_structures:
                lane_structures = [tower for tower in enemy_towers if tower.crown]
            lane_enemies = [
                enemy for enemy in enemies
                if not enemy.is_building
                and enemy.lane == unit.lane
                and (not enemy.flying or unit.can_target_air)
            ]
            close_enemies = [
                enemy for enemy in lane_enemies
                if math.hypot(enemy.x-unit.x, enemy.y-unit.y) <= 150
            ]
            nearby_taunts = [
                structure for structure in enemy_structures
                if getattr(structure, "stats", {}).get("taunt", False)
                and math.hypot(structure.x-unit.x, structure.y-unit.y) <= 240
            ]

            if unit.targets == "buildings":
                targets = lane_structures or enemy_structures
            elif nearby_taunts:
                targets = nearby_taunts
            elif close_enemies:
                targets = close_enemies
            else:
                targets = lane_structures

            if targets:
                target = min(
                    targets,
                    key=lambda candidate: math.hypot(
                        candidate.x-unit.x, candidate.y-unit.y
                    ),
                )
            else:
                target = None

            if target:
                distance = math.hypot(target.x-unit.x, target.y-unit.y)
                target_size = getattr(target, "size", getattr(target, "radius", 24))
                if distance <= unit.range + target_size:
                    unit.attack_timer -= dt
                    if unit.attack_timer <= 0:
                        unit.attack_timer = unit.cooldown
                        unit.attack_phase = unit.cooldown
                        if unit.range > 55:
                            self.projectiles.append({
                                "x": unit.x, "y": unit.y,
                                "tx": target.x, "ty": target.y,
                                "damage": unit.damage, "target": target,
                                "color": unit.color, "side": unit.side,
                                "splash": unit.stats.get("splash", 0),
                                "slow_duration": unit.stats.get("slow_duration", 0),
                            })
                        else:
                            self.damage_target(target, unit.damage)
                            if (isinstance(target, Unit)
                                    and unit.stats.get("slow_duration")):
                                target.slow_timer = max(
                                    target.slow_timer,
                                    unit.stats["slow_duration"],
                                )
                            self.damage_splash(
                                unit.side, target.x, target.y, unit.damage,
                                unit.stats.get("splash", 0), target,
                            )
                else:
                    bridge_x = BRIDGES[unit.lane]
                    target_across_river = (
                        (unit.side == "player" and target.y < 335)
                        or (unit.side == "bot" and target.y > 265)
                    )
                    needs_bridge = not unit.flying and not unit.crossed_bridge and (
                        target_across_river or not isinstance(target, Unit)
                    )
                    if needs_bridge and abs(unit.x-bridge_x) > 8:
                        goal_x, goal_y = bridge_x, 350 if unit.side == "player" else 250
                    elif needs_bridge:
                        goal_x, goal_y = bridge_x, 250 if unit.side == "player" else 350
                    elif isinstance(target, Unit) and not target.is_building:
                        goal_x, goal_y = target.x, target.y
                    else:
                        goal_x, goal_y = target.x, target.y
                    move_x, move_y = goal_x-unit.x, goal_y-unit.y
                    move_distance = math.hypot(move_x, move_y)
                    if move_distance > 0:
                        move_speed = unit.speed * (0.5 if unit.slow_timer else 1)
                        step = min(move_speed*dt, move_distance)
                        unit.x += move_x/move_distance*step
                        unit.y += move_y/move_distance*step
            elif not unit.is_building:
                bridge_x = BRIDGES[unit.lane]
                if not unit.crossed_bridge:
                    if abs(unit.x-bridge_x) > 8:
                        goal_x, goal_y = bridge_x, 350 if unit.side == "player" else 250
                    else:
                        goal_x, goal_y = bridge_x, 250 if unit.side == "player" else 350
                else:
                    enemy_side_y = 75 if unit.side == "player" else 525
                    enemy_goal_x = max(140, min(820, unit.x))
                    goal_x, goal_y = enemy_goal_x, enemy_side_y
                move_x, move_y = goal_x-unit.x, goal_y-unit.y
                move_distance = math.hypot(move_x, move_y)
                if move_distance:
                    move_speed = unit.speed * (0.5 if unit.slow_timer else 1)
                    step = min(move_speed*dt, move_distance)
                    unit.x += move_x/move_distance*step
                    unit.y += move_y/move_distance*step

            unit.x = max(140, min(820, unit.x))
            unit.y = max(80, min(520, unit.y))

        for index, unit in enumerate(self.units):
            for other in self.units[index+1:]:
                if unit.side != other.side:
                    continue
                dx, dy = other.x-unit.x, other.y-unit.y
                distance = math.hypot(dx, dy)
                minimum = (unit.size + other.size) * 0.78
                if 0 < distance < minimum:
                    if unit.is_building or other.is_building:
                        continue
                    push = (minimum-distance) * 0.5
                    unit.x -= dx/distance*push
                    unit.y -= dy/distance*push
                    other.x += dx/distance*push
                    other.y += dy/distance*push

        for projectile in self.projectiles[:]:
            target = projectile.get("target")
            if target is not None and getattr(target, "hp", 0) > 0:
                projectile["tx"] = target.x
                projectile["ty"] = target.y
            dx = projectile["tx"]-projectile["x"]
            dy = projectile["ty"]-projectile["y"]
            distance = math.hypot(dx, dy)
            if distance < 10:
                if projectile.get("spell_kind"):
                    self.resolve_spell_projectile(projectile)
                elif target is not None and getattr(target, "hp", 0) > 0:
                    self.damage_target(target, projectile["damage"])
                    if isinstance(target, Unit) and projectile.get("slow_duration"):
                        target.slow_timer = max(
                            target.slow_timer, projectile["slow_duration"]
                        )
                    self.damage_splash(
                        projectile["side"], projectile["target"].x,
                        projectile["target"].y, projectile["damage"],
                        projectile.get("splash", 0), projectile["target"],
                    )
                self.projectiles.remove(projectile)
            else:
                speed = projectile.get("speed", 230)
                projectile["x"] += dx/distance*speed*dt
                projectile["y"] += dy/distance*speed*dt

        for tower in self.towers:
            if tower.hp <= 0 or (tower.crown and not tower.activated):
                continue
            tower.cooldown -= dt
            if tower.cooldown <= 0:
                enemies = [u for u in self.units if u.side != tower.side
                           and math.hypot(u.x-tower.x, u.y-tower.y) < 170]
                if enemies:
                    target = min(enemies, key=lambda u: math.hypot(u.x-tower.x, u.y-tower.y))
                    self.projectiles.append({
                        "x": tower.x, "y": tower.y,
                        "tx": target.x, "ty": target.y,
                        "damage": 42, "target": target,
                        "color": "#f4d35e", "side": tower.side,
                    })
                    tower.cooldown = 0.85

        for effect in self.effects[:]:
            effect["life"] -= dt
            if effect["life"] <= 0:
                self.effects.remove(effect)

        destroyed_king_sides = set()
        destroyed_tower_sides = set()
        for tower in self.towers[:]:
            if tower.hp <= 0 and tower in self.towers:
                destroyed_tower_sides.add(tower.side)
                if tower.crown:
                    destroyed_king_sides.add(tower.side)
                if tower.side == "player":
                    self.bot_crowns = min(3, self.bot_crowns + (3 if tower.crown else 1))
                elif tower.side == "bot":
                    self.player_crowns = min(3, self.player_crowns + (3 if tower.crown else 1))
                if not tower.crown and tower.lane in (0, 1):
                    if tower.side == "bot":
                        self.player_expanded_lanes.add(tower.lane)
                    else:
                        self.bot_expanded_lanes.add(tower.lane)
                elif tower.crown:
                    if tower.side == "bot":
                        self.player_expanded_lanes.update((0, 1))
                    else:
                        self.bot_expanded_lanes.update((0, 1))
                tower.hp = -1
                self.towers.remove(tower)
                self.effects.append({"x": tower.x, "y": tower.y, "life": 1.0,
                                     "color": "#d9b46a", "radius": 55})

        if destroyed_king_sides == {"player"}:
            self.end_game("bot")
            return
        if destroyed_king_sides == {"bot"}:
            self.end_game("player")
            return
        if destroyed_king_sides == {"player", "bot"}:
            self.end_game()
            return
        if self.overtime and destroyed_tower_sides:
            player_hp = sum(max(0, tower.hp) for tower in self.towers
                            if tower.side == "player")
            bot_hp = sum(max(0, tower.hp) for tower in self.towers
                         if tower.side == "bot")
            self.end_game(overtime_tower_winner(
                destroyed_tower_sides, player_hp, bot_hp
            ))
            return
        if self.player_crowns >= 3 or self.bot_crowns >= 3:
            self.end_game()
            return
        if self.forced_winner:
            self.end_game(self.forced_winner)
            return
        if self.overtime:
            return
        if self.time_left <= 0 and not self.overtime:
            if self.player_crowns == self.bot_crowns:
                self.overtime = True
            else:
                self.end_game()

    def draw(self):
        arena = ARENAS[self.arena_index]
        ground, river, trim = arena[1], arena[2], arena[3]
        self.clear_canvas()
        self.canvas.configure(bg="#242622")

        # Textured field base and stone edging.
        self.canvas.create_rectangle(119, 65, 841, 525, fill="#332f27", outline="#d2bd86", width=5)
        self.canvas.create_rectangle(126, 72, 834, 518, fill=ground, outline="#756847", width=2)
        texture_style = self.arena_index // 20
        horror_level = 0 if self.arena_index < 5 else max(1, min(4, (self.arena_index - 5) // 10 + 1))
        for row in range(9):
            for col in range(14):
                x = 132 + col*50 + (row % 2)*12
                y = 78 + row*48
                if 264 <= y <= 337:
                    continue
                if texture_style == 0:
                    shade = ("#ffffff", "#000000", "#c5b277")[(row*7+col*3) % 3]
                    stipple = ("gray75", "gray50", "gray75")[(row+col) % 3]
                    self.canvas.create_oval(x, y, x+16, y+8, fill=shade,
                                            outline="", stipple=stipple)
                    self.canvas.create_line(x+19, y+5, x+25, y+1,
                                            fill=trim, width=1)
                elif texture_style < 3:
                    self.canvas.create_polygon(x, y+4, x+8, y-3, x+17, y+4,
                                               x+8, y+11, fill=trim, outline=ground)
                    self.canvas.create_line(x+20, y+2, x+29, y+8,
                                            fill=river, width=2)
                elif texture_style < 4:
                    self.canvas.create_rectangle(x, y, x+15, y+9,
                                                 fill=river, outline=trim)
                    self.canvas.create_oval(x+4, y+2, x+7, y+5,
                                            fill="#f2d986", outline="")
                    self.canvas.create_oval(x+9, y+2, x+12, y+5,
                                            fill="#f2d986", outline="")
                else:
                    self.canvas.create_oval(x, y, x+18, y+13,
                                            fill=river, outline=trim, width=1)
                    self.canvas.create_oval(x+4, y+4, x+7, y+8,
                                            fill="#fff0c2", outline="")
                    self.canvas.create_oval(x+11, y+4, x+14, y+8,
                                            fill="#fff0c2", outline="")

        if horror_level > 0:
            horror_marks = (
                (180, 210), (330, 430), (620, 180), (790, 410),
                (250, 470), (700, 310), (455, 390), (520, 150),
                (170, 330), (840, 225),
            )
            for mark_index, (x, y) in enumerate(horror_marks[:2+horror_level*2]):
                if 264 <= y <= 337:
                    y += 55 if y < 300 else -55
                if horror_level >= 1:
                    blood = "#8f2e2e" if horror_level < 3 else "#b43b35"
                    self.canvas.create_oval(x-16, y-5, x+18, y+7,
                                            fill=blood, outline="#5e2020", width=1)
                    self.canvas.create_line(x-13, y+3, x+14, y-2,
                                            fill="#652222", width=1)
                if horror_level >= 2 and mark_index % 2 == 0:
                    self.canvas.create_oval(x-9, y-12, x+9, y+5,
                                            fill="#d5cfb6", outline="#7b7869", width=1)
                    self.canvas.create_oval(x-4, y-7, x-1, y-4,
                                            fill="#50483d", outline="")
                    self.canvas.create_oval(x+1, y-7, x+4, y-4,
                                            fill="#50483d", outline="")
                    self.canvas.create_polygon(x-3, y+2, x+3, y+2,
                                               x+1, y+6, x-1, y+6,
                                               fill="#50483d", outline="")
                if horror_level >= 3:
                    self.canvas.create_rectangle(x-13, y-22, x+13, y-5,
                                                 fill="#4c4840", outline="#9b9481", width=2)
                    self.canvas.create_text(x, y-14, text="†",
                                            fill="#c9c0a5", font=("TkDefaultFont", 10, "bold"))
                if horror_level >= 4 and mark_index % 3 == 0:
                    self.canvas.create_oval(x-22, y-16, x+22, y+12,
                                            fill="#5a3330", outline="#32191a", width=2)
                    self.canvas.create_line(x-14, y+8, x+14, y-8,
                                            fill="#9d6a61", width=3)

        # River banks, water and two broad, plank-built bridges.
        self.canvas.create_rectangle(126, 258, 834, 342, fill="#344b3b", outline="")
        self.canvas.create_rectangle(126, 266, 834, 334, fill=river, outline="#bad2ae", width=2)
        for i in range(22):
            x = 137 + (i*37) % 685
            y = 272 + (i*23) % 52
            self.canvas.create_line(x, y, x+8+(i*11) % 17, y-2,
                                    fill="#b4d3c7", width=1)
        for bridge_x in BRIDGES:
            self.canvas.create_rectangle(bridge_x-34, 259, bridge_x+34, 341,
                                         fill="#493a2b", outline="#d3b477", width=3)
            for plank_y in range(264, 340, 11):
                self.canvas.create_line(bridge_x-31, plank_y, bridge_x+31, plank_y,
                                        fill="#bd9860", width=3)
            self.canvas.create_line(bridge_x-33, 263, bridge_x-33, 337,
                                    fill="#e1c48b", width=2)
            self.canvas.create_line(bridge_x+33, 263, bridge_x+33, 337,
                                    fill="#e1c48b", width=2)
        for x, y in ((170, 239), (330, 365), (790, 226), (620, 370), (160, 406),
                     (800, 390), (360, 185), (600, 174), (470, 385)):
            self.canvas.create_oval(x-9, y-5, x+8, y+5, fill="#817a61",
                                    outline="#c1b892", width=1)
            self.canvas.create_line(x-4, y-2, x+3, y-2, fill="#d0c9a4")

        # Deployment zones and invalid river surface.
        self.canvas.create_rectangle(128, 115, 832, 245, outline="#e5b7a9",
                         dash=(4, 5), width=1)
        self.canvas.create_rectangle(128, 350, 832, 516, outline="#bed7ab",
                                     dash=(4, 5), width=1)
        if hasattr(self, "player_expanded_lanes"):
            for lane in self.player_expanded_lanes:
                x1, x2 = (128, 474) if lane == 0 else (486, 832)
                self.canvas.create_rectangle(x1, 258, x2, 516,
                                             fill="#82d7a4", stipple="gray25",
                                             outline="#d3ffd6", dash=(6, 4), width=2)
        if hasattr(self, "bot_expanded_lanes"):
            for lane in self.bot_expanded_lanes:
                x1, x2 = (128, 474) if lane == 0 else (486, 832)
                self.canvas.create_rectangle(x1, 84, x2, 342,
                                             fill="#e58d7d", stipple="gray25",
                                             outline="#ffd3ca", dash=(6, 4), width=2)
        self.canvas.create_line(128, 245, 832, 245, fill="#e5b7a9", dash=(7, 5))
        self.canvas.create_line(128, 350, 832, 350, fill="#dce8c6", dash=(7, 5))

        if self.selected_card:
            card_data = CARDS[self.selected_card]
            is_spell = card_data.get("spell", False)
            lane = 0 if self.mouse_x < 480 else 1
            valid = ((130 <= self.mouse_x <= 830 and 70 <= self.mouse_y <= 530
                      and not 265 <= self.mouse_y <= 335) if is_spell else
                     self.deployment_zone_contains(
                         "player", self.mouse_x, self.mouse_y, lane
                     ))
            color = "#82ed99" if valid else "#f07669"
            radius = card_data["range"] if is_spell else card_data["size"]
            self.canvas.create_oval(self.mouse_x-radius, self.mouse_y-radius,
                                    self.mouse_x+radius, self.mouse_y+radius,
                                    outline=color, dash=(4, 3), width=2)
            self.canvas.create_text(480, 498, text="КЛИКНИ ПО ПОЛЮ ДЛЯ РАЗМЕЩЕНИЯ  •  ESC — ПАУЗА",
                                    fill=color, font=("TkDefaultFont", 10, "bold"))

        # Towers: layered stone bases, battlements, windows, banners and accurate collision bounds.
        for tower in self.towers:
            if tower.hp <= 0:
                continue
            player_side = tower.side == "player"
            banner = HERO_SKINS[self.skin_index][1] if player_side else "#bd6256"
            size = 28 if tower.crown else 21
            x, y = tower.x, tower.y
            self.canvas.create_oval(x-size-8, y+size-3, x+size+8, y+size+7,
                                    fill="#292820", outline="")
            self.canvas.create_rectangle(x-size-4, y-size+7, x+size+4, y+size+5,
                                         fill="#665442", outline="#d6c6a0", width=2)
            self.canvas.create_rectangle(x-size, y-size, x+size, y+size,
                                         fill="#a38d6a", outline="#eee0b6", width=2)
            self.canvas.create_rectangle(x-size+5, y-size+5, x+size-5, y+size,
                                         fill=banner, outline="#493f32", width=2)
            for crenel_x in (x-size+2, x-5, x+size-9):
                self.canvas.create_rectangle(crenel_x, y-size-5, crenel_x+7, y-size+4,
                                             fill="#c6b28c", outline="#f2e3bf")
            self.canvas.create_rectangle(x-5, y+2, x+5, y+size,
                                         fill="#3c372d", outline="#e4d1a2", width=1)
            self.canvas.create_oval(x-4, y-size+8, x+4, y-size+16,
                                    fill="#f0d47a", outline="#574c38")
            flag_y = y-size-12
            self.canvas.create_line(x, flag_y, x, flag_y+15, fill="#f2deb1", width=2)
            self.canvas.create_polygon(x, flag_y, x+15, flag_y+4, x, flag_y+8,
                                       fill=banner, outline="#f2deb1")
            if tower.crown and tower.activated:
                self.canvas.create_oval(x-10, y-size-20, x+10, y-size,
                                        fill="#e2bd82", outline="#44382b", width=2)
                self.canvas.create_rectangle(x-12, y-size-22, x+12, y-size-17,
                                             fill="#e9c95f", outline="#493c28")
                self.canvas.create_line(x+8, y-size-7, x+25, y-size-13,
                                        fill="#34302a", width=5)
                self.canvas.create_oval(x+20, y-size-18, x+29, y-size-9,
                                        fill="#9a8b73", outline="#eee0b6")

            bar_width = 62 if tower.crown else 54
            bar_y = tower_health_bar_y(tower)
            self.canvas.create_rectangle(x-bar_width/2, bar_y,
                                         x+bar_width/2, bar_y+7,
                                         fill="#242622", outline="#f1e4c4", width=1)
            hp_fraction = max(0, tower.hp/tower.max_hp)
            self.canvas.create_rectangle(x-bar_width/2+2, bar_y+2,
                                         x-bar_width/2+2+(bar_width-4)*hp_fraction,
                                         bar_y+5,
                                         fill="#7bd576" if hp_fraction > .35 else "#e47b68",
                                         outline="")
            if self.show_hitboxes:
                self.canvas.create_oval(x-tower.radius, y-tower.radius,
                                        x+tower.radius, y+tower.radius,
                                        outline="#fffb83", dash=(3, 3), width=2)

        # Units with distinct silhouettes, shadows and readable health bars.
        for unit in self.units:
            x, y, size = unit.x, unit.y, unit.size
            walk_bob = math.sin(unit.walk_phase) * (2 if not unit.is_building else 0)
            y += walk_bob
            attack_shift = 3 if unit.attack_phase > 0 else 0
            x += attack_shift if unit.side == "player" else -attack_shift
            player_side = unit.side == "player"
            body = HERO_SKINS[self.skin_index][1] if player_side and unit.card == "Рыцарь" else unit.color
            trim_color = "#9ec8f4" if player_side else "#f09b87"
            element = elemental_type(unit.card)
            if unit.stats.get("ice_aura"):
                self.canvas.create_oval(x-78, y-78, x+78, y+78,
                                        outline="#a8edff", dash=(2, 5), width=2)
            rarity_color = unit.stats.get("rarity_color", "#a9adb5")
            self.canvas.create_oval(x-size-3, y-size-3, x+size+3, y+size+3,
                                    outline=rarity_color, width=2)
            self.canvas.create_oval(x-size, y+size*.45, x+size, y+size+5,
                                    fill="#302c24", outline="")
            if unit.is_building:
                self.canvas.create_rectangle(x-size, y-size, x+size, y+size,
                                             fill=body, outline="#4a3e30", width=2)
                self.canvas.create_rectangle(x-size*.55, y-size*.55,
                                             x+size*.55, y+size*.55,
                                             fill="#554a3b", outline="#e5d4aa", width=2)
                if unit.card == "Клетка с гоблином":
                    for bar_x in (-size*.3, 0, size*.3):
                        self.canvas.create_line(x+bar_x, y-size*.5,
                                                x+bar_x, y+size*.5,
                                                fill="#ead9ad", width=2)
                else:
                    self.canvas.create_line(x, y, x+size*1.35, y-size*.8,
                                            fill="#d5c6a0", width=4)
                    self.canvas.create_oval(x+size*.9, y-size,
                                            x+size*1.55, y-size*.45,
                                            fill="#d6b66e", outline="#4a3e30", width=2)
            elif unit.flying:
                self.canvas.create_polygon(x, y, x-size-8, y-size*.65,
                                           x-size*.35, y+size*.15,
                                           fill=body, outline=trim_color)
                self.canvas.create_polygon(x, y, x+size+8, y-size*.65,
                                           x+size*.35, y+size*.15,
                                           fill=body, outline=trim_color)
                self.canvas.create_oval(x-size*.65, y-size*.55,
                                        x+size*.65, y+size*.55,
                                        fill=body, outline=trim_color, width=2)
                self.canvas.create_oval(x-size*.8, y-size*.85,
                                        x-size*.15, y-size*.2,
                                        fill="#e3c18d", outline="#594638")
                if element == "fire":
                    self.canvas.create_polygon(x-size*.35, y+size*.3,
                                               x-size*.7, y-size*.2,
                                               x-size*.35, y-size*.3,
                                               x-size*.25, y-size*.85,
                                               x+size*.05, y-size*.25,
                                               x+size*.38, y-size*.55,
                                               x+size*.55, y+size*.18,
                                               fill="#e85c36", outline="#ffd16b", width=2)
                    self.canvas.create_polygon(x-size*.18, y+size*.15,
                                               x-size*.06, y-size*.35,
                                               x+size*.2, y+size*.15,
                                               fill="#ffe58a", outline="")
                elif element == "ice":
                    self.canvas.create_polygon(x, y-size*.95,
                                               x-size*.35, y-size*.35,
                                               x, y-size*.48,
                                               x+size*.38, y-size*.25,
                                               fill="#a9edff", outline="#efffff", width=2)
                    self.canvas.create_polygon(x-size*.68, y-size*.1,
                                               x-size*.95, y-size*.55,
                                               x-size*.38, y-size*.25,
                                               fill="#73bedb", outline="#efffff")
                elif element == "lightning":
                    for direction in (-1, 1):
                        self.canvas.create_line(
                            x+direction*size*.55, y-size*.55,
                            x+direction*size*1.05, y-size*.15,
                            x+direction*size*.72, y+size*.12,
                            x+direction*size*1.18, y+size*.55,
                            fill="#e4faff", width=2,
                        )
                elif element == "water":
                    for direction in (-1, 1):
                        self.canvas.create_line(
                            x+direction*size*.25, y+size*.3,
                            x+direction*size*.58, y+size*.85,
                            x+direction*size*.92, y+size*.55,
                            fill="#80c9e8", width=3, smooth=True,
                        )
            else:
                model = unit.stats.get("model", 0)
                is_elemental_model = element in ("fire", "ice", "lightning", "water")
                if unit.card.startswith("Хоббихорсер"):
                    horse_body = "#b6a079"
                    stick_color = "#805b3d"
                    self.canvas.create_line(x-size*.08, y+size*.2,
                                            x-size*.02, y+size*1.35,
                                            fill=stick_color, width=max(3, size*.22))
                    self.canvas.create_line(x-size*.32, y+size*.62,
                                            x+size*.24, y+size*.68,
                                            fill="#d5bd8c", width=2)
                    self.canvas.create_oval(x-size*.95, y-size*.35,
                                            x+size*.95, y+size*.55,
                                            fill=horse_body, outline=trim_color, width=2)
                    self.canvas.create_polygon(x+size*.45, y-size*.2,
                                               x+size*1.35, y-size*.75,
                                               x+size*1.15, y-size*.05,
                                               fill=horse_body, outline=trim_color)
                    self.canvas.create_polygon(x+size*.98, y-size*.43,
                                               x+size*1.13, y-size*.9,
                                               x+size*1.25, y-size*.42,
                                               x+size*1.43, y-size*.78,
                                               x+size*1.43, y-size*.25,
                                               fill="#594239", outline="#382f2a")
                    self.canvas.create_oval(x+size*1.05, y-size*.58,
                                            x+size*1.43, y-size*.23,
                                            fill="#d3b88a", outline="#594638", width=2)
                    self.canvas.create_oval(x+size*1.12, y-size*.58,
                                            x+size*1.2, y-size*.5,
                                            fill="#211f1d", outline="")
                    self.canvas.create_line(x+size*.85, y-size*.48,
                                            x+size*1.4, y-size*.35,
                                            fill="#603e31", width=2)
                    self.canvas.create_line(x+size*1.25, y-size*.34,
                                            x+size*.58, y+size*.8,
                                            fill="#603e31", width=2)
                    for leg_x in (-size*.65, size*.65):
                        self.canvas.create_line(x+leg_x, y+size*.35,
                                                x+leg_x-size*.12, y+size*1.15,
                                                fill=trim_color, width=3)
                    self.canvas.create_oval(x-size*.22, y-size*.95,
                                            x+size*.22, y-size*.35,
                                            fill="#e8c793", outline=trim_color, width=2)
                    self.canvas.create_polygon(x-size*.5, y-size*.45,
                                               x-size*.65, y+size*.55,
                                               x+size*.56, y+size*.55,
                                               x+size*.25, y-size*.48,
                                               fill=body, outline=trim_color, width=2)
                    self.canvas.create_polygon(x-size*.18, y-size*.77,
                                               x-size*.55, y-size*1.25,
                                               x+size*.12, y-size*.75,
                                               fill=body, outline=trim_color)
                elif (unit.card.startswith("Фурри") or unit.card.startswith("Кот-батон")
                      or "кот" in unit.card.lower()):
                    self.canvas.create_polygon(x-size*.45, y-size*.15,
                                               x-size*.15, y-size*.85,
                                               x+size*.15, y-size*.85,
                                               x+size*.45, y-size*.15,
                                               x+size*.55, y+size,
                                               x-size*.55, y+size,
                                               fill=body, outline=trim_color, width=2)
                    self.canvas.create_oval(x-size*.58, y-size*1.35,
                                            x+size*.58, y-size*.25,
                                            fill="#dfc79d", outline=trim_color, width=2)
                    for ear_x in (-size*.38, size*.38):
                        ear_y = y-size*1.08
                        self.canvas.create_polygon(x+ear_x, ear_y,
                                                   x+ear_x-size*.24, ear_y-size*.62,
                                                   x+ear_x+size*.16, ear_y-size*.18,
                                                   fill=body, outline=trim_color)
                        self.canvas.create_polygon(x+ear_x-size*.11, ear_y-size*.13,
                                                   x+ear_x-size*.2, ear_y-size*.43,
                                                   x+ear_x+size*.04, ear_y-size*.2,
                                                   fill="#e994a8", outline="")
                    self.canvas.create_oval(x-size*.34, y-size*.78,
                                            x-size*.02, y-size*.48,
                                            fill="#f0d7c9", outline="")
                    self.canvas.create_oval(x+size*.02, y-size*.78,
                                            x+size*.34, y-size*.48,
                                            fill="#f0d7c9", outline="")
                    self.canvas.create_oval(x-size*.27, y-size*.91,
                                            x-size*.13, y-size*.72,
                                            fill="#fff1b9", outline="")
                    self.canvas.create_oval(x+size*.13, y-size*.91,
                                            x+size*.27, y-size*.72,
                                            fill="#fff1b9", outline="")
                    self.canvas.create_oval(x-size*.22, y-size*.88,
                                            x-size*.17, y-size*.77,
                                            fill="#24201e", outline="")
                    self.canvas.create_oval(x+size*.17, y-size*.88,
                                            x+size*.22, y-size*.77,
                                            fill="#24201e", outline="")
                    self.canvas.create_polygon(x-size*.08, y-size*.48,
                                               x+size*.08, y-size*.48,
                                               x, y-size*.38,
                                               fill="#d67883", outline="")
                    self.canvas.create_line(x, y-size*.38, x, y-size*.3,
                                            fill="#594638", width=1)
                    for whisker_y in (-.43, -.32):
                        self.canvas.create_line(x-size*.18, y+size*whisker_y,
                                                x-size*.56, y+size*(whisker_y-.08),
                                                fill="#594638", width=1)
                        self.canvas.create_line(x+size*.18, y+size*whisker_y,
                                                x+size*.56, y+size*(whisker_y-.08),
                                                fill="#594638", width=1)
                    self.canvas.create_line(x-size*.5, y+size*.25,
                                            x-size*.9, y+size*.95,
                                            fill=body, width=4)
                    self.canvas.create_line(x+size*.5, y+size*.25,
                                            x+size*.9, y+size*.95,
                                            fill=body, width=4)
                    self.canvas.create_arc(x+size*.35, y-size*.05,
                                           x+size*1.25, y+size*.75,
                                           start=90, extent=150,
                                           style="arc", outline=body, width=5)
                elif element == "fire":
                    self.canvas.create_polygon(x-size*.7, y+size*.85,
                                               x-size*.55, y-size*.15,
                                               x-size*.3, y-size*.65,
                                               x-size*.08, y-size*1.35,
                                               x+size*.2, y-size*.65,
                                               x+size*.48, y-size*1.05,
                                               x+size*.72, y-size*.1,
                                               x+size*.62, y+size*.85,
                                               fill="#d94f32", outline="#ffc45b", width=2)
                    self.canvas.create_polygon(x-size*.3, y+size*.55,
                                               x-size*.12, y-size*.08,
                                               x+size*.08, y-size*.5,
                                               x+size*.32, y-size*.02,
                                               x+size*.38, y+size*.55,
                                               fill="#ffb43f", outline="#ffe58a")
                    self.canvas.create_oval(x-size*.23, y-size*.82,
                                            x+size*.23, y-size*.35,
                                            fill="#f2bd78", outline="#723d30", width=2)
                    self.canvas.create_oval(x-size*.13, y-size*.66,
                                            x-size*.06, y-size*.57,
                                            fill="#39211e", outline="")
                    self.canvas.create_oval(x+size*.06, y-size*.66,
                                            x+size*.13, y-size*.57,
                                            fill="#39211e", outline="")
                elif element == "ice":
                    self.canvas.create_polygon(x, y-size*1.18,
                                               x+size*.82, y-size*.46,
                                               x+size*.56, y+size*.65,
                                               x, y+size,
                                               x-size*.56, y+size*.65,
                                               x-size*.82, y-size*.46,
                                               fill="#73bedb", outline="#e5fbff", width=2)
                    self.canvas.create_polygon(x-size*.68, y-size*.36,
                                               x-size*1.1, y-size*.93,
                                               x-size*.28, y-size*.65,
                                               x, y-size*1.4,
                                               x+size*.3, y-size*.65,
                                               x+size*1.08, y-size*.97,
                                               x+size*.66, y-size*.27,
                                               fill="#b9efff", outline="#f2ffff", width=2)
                    for eye_x in (-size*.2, size*.2):
                        self.canvas.create_oval(x+eye_x-size*.05, y-size*.12,
                                                x+eye_x+size*.05, y+size*.02,
                                                fill="#264f70", outline="")
                elif element == "lightning":
                    self.canvas.create_polygon(x-size*.53, y-size*.75,
                                               x+size*.45, y-size*1.05,
                                               x+size*.05, y-size*.12,
                                               x+size*.62, y-size*.15,
                                               x-size*.42, y+size*.85,
                                               x-size*.12, y+size*.12,
                                               x-size*.72, y+size*.2,
                                               fill="#528ed6", outline="#e5fbff", width=2)
                    for direction in (-1, 1):
                        self.canvas.create_line(
                            x+direction*size*.5, y-size*.4,
                            x+direction*size*1.05, y-size*.12,
                            x+direction*size*.62, y+size*.15,
                            x+direction*size*1.12, y+size*.52,
                            fill="#b8f1ff", width=2,
                        )
                    self.canvas.create_oval(x-size*.06, y-size*.55,
                                            x+size*.06, y-size*.42,
                                            fill="#fff9bb", outline="")
                elif element == "water":
                    self.canvas.create_oval(x-size*.58, y-size*.86,
                                            x+size*.58, y+size*.05,
                                            fill="#567fc4", outline="#b9e8ff", width=2)
                    self.canvas.create_oval(x-size*.29, y-size*.57,
                                            x+size*.29, y-size*.02,
                                            fill="#80c9e8", outline="#e6faff")
                    for tentacle in (-2, -1, 0, 1, 2):
                        start_x = x + tentacle * size*.2
                        self.canvas.create_line(
                            start_x, y,
                            start_x+tentacle*size*.12, y+size*.58,
                            start_x+tentacle*size*.08, y+size,
                            fill="#6574c8", width=3, smooth=True,
                        )
                    for eye_x in (-size*.12, size*.12):
                        self.canvas.create_oval(x+eye_x-size*.04, y-size*.45,
                                                x+eye_x+size*.04, y-size*.34,
                                                fill="#fff3c1", outline="")
                elif model % 6 == 0:
                    self.canvas.create_polygon(x-size*.8, y, x-size*.35, y-size,
                                               x+size*.35, y-size, x+size*.8, y,
                                               x+size*.35, y+size, x-size*.35, y+size,
                                               fill=body, outline=trim_color, width=2)
                elif model % 6 == 1:
                    self.canvas.create_oval(x-size, y-size*.75, x+size, y+size,
                                            fill=body, outline=trim_color, width=2)
                    self.canvas.create_polygon(x-size*.7, y-size*.55,
                                               x-size*.35, y-size*1.35,
                                               x, y-size*.65,
                                               fill=trim_color, outline=trim_color)
                elif model % 6 == 2:
                    self.canvas.create_rectangle(x-size*.75, y-size,
                                                 x+size*.75, y+size,
                                                 fill=body, outline=trim_color, width=2)
                    self.canvas.create_rectangle(x-size*.45, y-size*1.15,
                                                 x+size*.45, y-size*.6,
                                                 fill="#e8c793", outline=trim_color)
                elif model % 6 == 3:
                    self.canvas.create_polygon(x, y-size*1.2, x+size, y-size*.25,
                                               x+size*.65, y+size,
                                               x-size*.65, y+size,
                                               x-size, y-size*.25,
                                               fill=body, outline=trim_color, width=2)
                elif model % 6 == 4:
                    self.canvas.create_oval(x-size*.75, y-size*.75,
                                            x+size*.75, y+size,
                                            fill=body, outline=trim_color, width=2)
                    self.canvas.create_oval(x-size*1.05, y-size*.55,
                                            x-size*.55, y-size*.05,
                                            fill=body, outline=trim_color)
                    self.canvas.create_oval(x+size*.55, y-size*.55,
                                            x+size*1.05, y-size*.05,
                                            fill=body, outline=trim_color)
                else:
                    self.canvas.create_polygon(x-size*.9, y+size*.8,
                                               x-size*.55, y-size*.9,
                                               x, y-size*.35,
                                               x+size*.55, y-size*.9,
                                               x+size*.9, y+size*.8,
                                               fill=body, outline=trim_color, width=2)
                head_size = max(5, size*.48)
                is_furry = (unit.card.startswith("Фурри")
                            or unit.card.startswith("Кот-батон")
                            or "кот" in unit.card.lower())
                if not is_furry and not is_elemental_model:
                    self.canvas.create_oval(x-head_size, y-size*.82,
                                            x+head_size, y-size*.82+head_size*2,
                                            fill="#e3c18d", outline="#594638", width=1)
                self.canvas.create_arc(x-size, y-size*.65, x+size, y+size*.85,
                                       start=190, extent=160, style="arc",
                                       outline="#f5d477", width=2)
                if unit.card in ("Рыцарь", "Страж", "Великан", "Тролль"):
                    self.canvas.create_polygon(x-size*.65, y-size*.65,
                                               x, y-size*1.35,
                                               x+size*.65, y-size*.65,
                                               fill="#d4c09a", outline="#514638")
            is_furry = (unit.card.startswith("Фурри")
                        or unit.card.startswith("Кот-батон")
                        or "кот" in unit.card.lower())
            is_horse = unit.card.startswith("Хоббихорсер")
            if (not unit.is_building and not unit.flying
                    and not is_furry and not is_horse and not is_elemental_model):
                self.draw_character_face(unit.card, unit.stats, x, y, size)
            if not unit.is_building and not unit.flying:
                accent, _, _, _ = self.character_skin_style(unit.card, unit.stats)
                if element != "water":
                    self.draw_profile_weapon(
                        x, y, size, accent, -1 if is_horse or is_furry else 1,
                        (sum(map(ord, unit.card))
                         + unit.stats.get("model", 0)*5) % 5,
                        unit.range > 55,
                    )
                self.draw_character_texture(
                    unit.card, unit.stats, x, y+size*.1, size
                )

            if unit.card == "67-Мем-стример":
                for trail_index in range(3):
                    trail_y = y-size*(1.15 + trail_index*.75) + math.sin(
                        unit.walk_phase + trail_index*1.7) * size*.35
                    trail_x = x + math.cos(unit.walk_phase + trail_index*2) * size*.9
                    self.canvas.create_text(trail_x, trail_y, text="67",
                                            fill="#263c52",
                                            font=("TkDefaultFont", max(8, int(size*.75)+2), "bold"))
                    self.canvas.create_text(trail_x, trail_y, text="67",
                                            fill="#67d9ff",
                                            font=("TkDefaultFont", max(8, int(size*.75)), "bold"))

            health_width = max(28, size*2.7)
            bar_y = y-size-12
            fraction = max(0, min(1, unit.hp/unit.max_hp))
            self.canvas.create_rectangle(x-health_width/2, bar_y,
                                         x+health_width/2, bar_y+5,
                                         fill="#332c29", outline="#e5dbb9")
            self.canvas.create_rectangle(x-health_width/2+1, bar_y+1,
                                         x-health_width/2+1+(health_width-2)*fraction,
                                         bar_y+4, fill="#79d274", outline="")
            if self.show_hitboxes:
                self.canvas.create_oval(x-size, y-size, x+size, y+size,
                                        outline="#fff784", dash=(2, 3), width=2)

        for projectile in self.projectiles:
            x, y = projectile["x"], projectile["y"]
            color = projectile["color"]
            visual = projectile.get("visual")
            if visual in ("fireball", "furry_fireball", "horse_fireball"):
                if visual == "furry_fireball":
                    self.canvas.create_oval(x-14, y-14, x+14, y+14,
                                            fill=color, outline="#f6a9dc", width=3)
                    for sparkle_x in (-9, 9):
                        self.canvas.create_polygon(x+sparkle_x, y-12,
                                                   x+sparkle_x+4, y-4,
                                                   x+sparkle_x, y+4,
                                                   x+sparkle_x-4, y-4,
                                                   fill="#fff0b2", outline="")
                elif visual == "horse_fireball":
                    self.canvas.create_oval(x-15, y-11, x+15, y+11,
                                            fill=color, outline="#f2dfae", width=3)
                    self.canvas.create_polygon(x-10, y+8, x, y-12,
                                               x+10, y+8, x+5, y+14,
                                               x-5, y+14,
                                               fill="#7d623e", outline="#ead8aa")
                else:
                    self.canvas.create_oval(x-12, y-12, x+12, y+12,
                                            fill=color, outline="#fff2c4", width=2)
                self.canvas.create_polygon(x-7, y+7, x-12, y+20,
                                           x+1, y+14, x+10, y+20,
                                           x+7, y+6, fill="#ffdb68", outline="")
                self.canvas.create_oval(x-4, y-5, x+3, y+2,
                                        fill="#fff2c4", outline="")
            elif visual == "barrel":
                self.canvas.create_oval(x-12, y-8, x+12, y+8,
                                        fill=color, outline="#f2d47b", width=2)
                self.canvas.create_line(x-5, y-7, x-5, y+7,
                                        fill="#e1bd78", width=2)
                self.canvas.create_line(x+5, y-7, x+5, y+7,
                                        fill="#e1bd78", width=2)
            else:
                self.canvas.create_line(x-5, y+4, x+5, y-4,
                                        fill="#fff3ca", width=4)
                self.canvas.create_oval(x-4, y-4, x+4, y+4,
                                        fill=color, outline="#fff2c4")

        for effect in self.effects:
            x, y = effect["x"], effect["y"]
            radius = int(effect["radius"] * max(0.15, effect["life"]/0.55))
            self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                                    outline=effect["color"], width=3)
            self.canvas.create_oval(x-radius*.65, y-radius*.65,
                                    x+radius*.65, y+radius*.65,
                                    outline="#fff0b2", width=1)
            if effect.get("corpse"):
                horror = effect.get("horror", 2)
                self.canvas.create_oval(x-18, y+4, x+20, y+11,
                                        fill="#6e2424", outline="#421717", width=1)
                self.canvas.create_oval(x-12, y-10, x+12, y+8,
                                        fill="#9c765f", outline="#50392e", width=1)
                self.canvas.create_line(x-15, y+5, x+15, y-4,
                                        fill="#4f3830", width=4)
                if horror >= 3:
                    self.canvas.create_polygon(x-8, y-8, x, y-20,
                                               x+8, y-8, x+4, y,
                                               x-4, y,
                                               fill="#d8d0b6", outline="#77715e")

        # Stone HUD, crown counter and elixir meter.
        self.canvas.create_rectangle(0, 0, WIDTH, 65, fill="#292722", outline="#d5bc83", width=2)
        self.canvas.create_text(215, 22, text=f"ВАШИ КОРОНЫ  {self.player_crowns}",
                                fill="#92c5fa", font=("TkDefaultFont", 12, "bold"))
        if self.overtime:
            timer_text = overtime_timer_text(self.overtime_left)
        else:
            timer_text = (
                f"{max(0, int(self.time_left//60))}:"
                f"{max(0, int(self.time_left%60)):02d}"
            )
        self.canvas.create_text(480, 21, text=timer_text,
                                fill="#fff0c2", font=("TkDefaultFont", 20, "bold"))
        self.canvas.create_text(745, 22, text=f"{self.bot_name}  Ур.{self.bot_level}  {self.bot_crowns}",
                                fill="#f0a08d", font=("TkDefaultFont", 12, "bold"))
        elixir_label = "ЭЛИКСИР x2" if self.overtime or self.time_left <= 60 else "ЭЛИКСИР"
        self.canvas.create_text(80, 52, text=f"{elixir_label} {self.player_elixir:.1f}/10",
                                fill="#f3c9f1", font=("TkDefaultFont", 9, "bold"))
        for i in range(10):
            x = 147+i*18
            fill = "#cf58bd" if self.player_elixir >= i+1 else "#554653"
            self.canvas.create_rectangle(x, 46, x+13, 59, fill=fill,
                                         outline="#d79bd1", width=1)
            bot_x = 633+i*18
            bot_fill = "#68aeca" if self.bot_elixir >= i+1 else "#42525a"
            self.canvas.create_rectangle(bot_x, 46, bot_x+13, 59,
                                         fill=bot_fill, outline="#b4d7e4", width=1)
        self.canvas.create_text(405, 52, text=f"МОНЕТЫ {self.gold}",
                                fill="#f3d37a", font=("TkDefaultFont", 9, "bold"))
        self.canvas.create_text(870, 52, text=f"БОТ {self.bot_elixir:.1f}/10",
                                fill="#b4d7e4", font=("TkDefaultFont", 9, "bold"))
        self.canvas.create_text(915, 14, text="H: ХИТБОКСЫ",
                                fill="#bdb6a4", font=("TkDefaultFont", 8))
        if self.notice:
            self.canvas.create_rectangle(310, 73, 650, 98,
                                         fill="#302b24", outline="#e0bf78", width=1)
            self.canvas.create_text(480, 85, text=self.notice, fill="#ffe5a0",
                                    font=("TkDefaultFont", 9, "bold"))

        # Card tray is drawn last so it always receives clicks above the arena.
        self.canvas.create_rectangle(0, 522, WIDTH, HEIGHT, fill="#292722",
                                     outline="#c7ac75", width=2)
        for i, card in enumerate(self.hand):
            data = CARDS[card]
            x1, y1 = 255+i*120, 530
            x2, y2 = x1+112, 592
            selected = card == self.selected_card
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         fill="#fff2cb" if selected else "#d9c99e",
                                         outline="#e1c46d" if selected else "#6c624e",
                                         width=3 if selected else 2)
            self.canvas.create_oval(x1+7, y1+7, x1+31, y1+31,
                                    fill=data["color"], outline="#453c30", width=2)
            self.canvas.create_text(x1+19, y1+19, text="✦" if data.get("spell") else "●",
                                    fill="#fff1c5", font=("TkDefaultFont", 9, "bold"))
            self.canvas.create_text(x1+38, y1+16, anchor="w", text=card,
                                    fill="#352f27", font=("TkDefaultFont", 8, "bold"))
            cost_color = "#a33d9a" if data["cost"] <= self.player_elixir else "#77736b"
            self.canvas.create_oval(x1+8, y1+36, x1+30, y1+58,
                                    fill=cost_color, outline="#fff1c5", width=1)
            self.canvas.create_text(x1+19, y1+47, text=str(data["cost"]),
                                    fill="#fff4ff", font=("TkDefaultFont", 10, "bold"))
            self.canvas.create_text(x2-12, y2-10, text=str(i+1), fill="#786f5c",
                                    font=("TkDefaultFont", 8, "bold"))
            if data["cost"] > self.player_elixir:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#202020",
                                             stipple="gray50", outline="")

        if self.paused:
            self.canvas.create_rectangle(280, 205, 680, 410, fill="#312c31",
                                         outline="#d8c077", width=3)
            self.canvas.create_text(480, 245, text="ПАУЗА", fill="#fff2c4",
                                    font=("TkDefaultFont", 30, "bold"))
            self.button(330, 278, 630, 328, "ПРОДОЛЖИТЬ", "#d8c077", "#312c31",
                        lambda: setattr(self, "paused", False))
            self.button(330, 342, 630, 392, "В МЕНЮ", "#b8a1b3", "#312c31",
                        self.show_menu)
        self.apply_canvas_scale()

    def end_game(self, forced_winner=None):
        if not self.running:
            return
        self.running = False
        self.loop_token += 1
        self.screen = "result"
        self.battles_played += 1
        self.crowns_earned += self.player_crowns
        won = battle_player_won(
            self.player_crowns, self.bot_crowns,
            self.player_elixir, self.bot_elixir, forced_winner,
        )
        previous_arena = self.arena_index
        if won:
            self.wins += 1
            self.chests += 1
            battle_reward = battle_gold_reward(self.trophies, True)
            self.gold += battle_reward
            self.trophies += 30
            self.last_reward = f"Победа! +30 кубков, сундук и {battle_reward} золота."
        else:
            battle_reward = battle_gold_reward(self.trophies, False)
            self.gold += battle_reward
            self.trophies = max(0, self.trophies - 15)
            self.last_reward = f"За бой получено {battle_reward} золота. Кубки: -15."
        self.best_trophies = max(self.best_trophies, self.trophies)
        self.arena_index = arena_for_trophies(self.best_trophies)
        new_arenas = self.arena_index - previous_arena
        if new_arenas > 0:
            self.gold += new_arenas * 100
            self.chests += new_arenas
            unlocked = []
            for _ in range(new_arenas):
                locked_cards = [name for name in CARDS
                                if name not in self.unlocked_cards]
                if locked_cards:
                    card = random.choice(locked_cards)
                    self.unlocked_cards.append(card)
                    unlocked.append(card)
            self.last_reward += (
                f" Новая арена! Награда: +{new_arenas * 100} золота, "
                f"+{new_arenas} сундук(а)."
            )
            if unlocked:
                self.last_reward += f" Открыта карта: {unlocked[0]}"
        pass_xp_gained = 25 + self.player_crowns*15 + (25 if won else 0)
        previous_tier = self.battle_pass_xp // 100 + 1
        self.battle_pass_xp += pass_xp_gained
        current_tier = self.battle_pass_xp // 100 + 1
        tiers_gained = range(previous_tier + 1, current_tier + 1)
        tier_coins = 50 * len(tiers_gained)
        tier_chests = sum(1 for tier in tiers_gained if tier % 3 == 0)
        self.gold += tier_coins
        self.chests += tier_chests
        self.last_reward += f" БП: +{pass_xp_gained} XP"
        if tier_coins or tier_chests:
            self.last_reward += f", награда пропуска: +{tier_coins} монет"
            if tier_chests:
                self.last_reward += f" и {tier_chests} сундук."
            else:
                self.last_reward += "."
        score = self.player_crowns*1000 + int(self.player_elixir*100)
        self.best = max(self.best, score)
        self.save()

        self.clear_canvas()
        arena = ARENAS[self.arena_index]
        self.canvas.configure(bg=arena[1])
        self.canvas.create_text(480, 210, text="ПОБЕДА" if won else "ПОРАЖЕНИЕ",
                                fill="#f3d36b" if won else "#bd7a70",
                                font=("TkDefaultFont", 42, "bold"))
        self.canvas.create_text(480, 270,
                                text=f"Корон: {self.player_crowns}:{self.bot_crowns}",
                                fill="#fff2c4", font=("TkDefaultFont", 18))
        self.canvas.create_text(480, 303, text=self.last_reward,
                                fill="#f3d37a", font=("TkDefaultFont", 10, "bold"))
        self.button(330, 330, 630, 390, "ИГРАТЬ СНОВА", "#f3d36b", "#312c31",
                    lambda: self.start_game())
        self.button(330, 405, 630, 465, "В МЕНЮ", "#b8a1b3", "#312c31",
                    self.show_menu)
        self.apply_canvas_scale()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ClashArena().run()
