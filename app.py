import os
import random
import sqlite3
import threading
import asyncio

from datetime import datetime, timedelta

from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

WEB_APP_URL = os.getenv(
    "WEB_APP_URL",
    "https://carnival-reckless-canyon.ngrok-free.dev"
)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_PATH = os.path.join(
    BASE_DIR,
    "snake.db"
)

XP_PER_FOOD = 10

DAILY_REWARDS = [
    25,
    35,
    50,
    70,
    100,
    150,
    250
]

CHEST_COOLDOWN_HOURS = 24


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)


# ============================================================
# COIN SKINS
# ============================================================

COIN_SKINS = [

    {
        "id": "emerald",
        "name": "Изумруд",
        "price": 0,
        "color": "#22c55e",
        "rarity": "common"
    },

    {
        "id": "lapis",
        "name": "Лазурит",
        "price": 250,
        "color": "#2563eb",
        "rarity": "common"
    },

    {
        "id": "ruby",
        "name": "Рубин",
        "price": 500,
        "color": "#ef4444",
        "rarity": "rare"
    },

    {
        "id": "amethyst",
        "name": "Аметист",
        "price": 750,
        "color": "#a855f7",
        "rarity": "rare"
    },

    {
        "id": "gold",
        "name": "Золото",
        "price": 1000,
        "color": "#facc15",
        "rarity": "rare"
    },

    {
        "id": "ocean",
        "name": "Океан",
        "price": 1250,
        "color": "#06b6d4",
        "rarity": "rare"
    },

    {
        "id": "cosmos",
        "name": "Космос",
        "price": 1500,
        "color": "#6366f1",
        "rarity": "epic"
    },

    {
        "id": "fire",
        "name": "Огонь",
        "price": 1750,
        "color": "#f97316",
        "rarity": "epic"
    },

    {
        "id": "ice",
        "name": "Лёд",
        "price": 2000,
        "color": "#67e8f9",
        "rarity": "epic"
    },

    {
        "id": "forest",
        "name": "Лес",
        "price": 2250,
        "color": "#16a34a",
        "rarity": "epic"
    },

    {
        "id": "electric",
        "name": "Электричество",
        "price": 2500,
        "color": "#38bdf8",
        "rarity": "epic"
    },

    {
        "id": "moon",
        "name": "Луна",
        "price": 2750,
        "color": "#c4b5fd",
        "rarity": "epic"
    },

    {
        "id": "sun",
        "name": "Солнце",
        "price": 3000,
        "color": "#fb923c",
        "rarity": "epic"
    },

    {
        "id": "toxic",
        "name": "Токсик",
        "price": 3500,
        "color": "#84cc16",
        "rarity": "legendary"
    },

    {
        "id": "blood",
        "name": "Кровь",
        "price": 4000,
        "color": "#dc2626",
        "rarity": "legendary"
    },

    {
        "id": "saturn",
        "name": "Сатурн",
        "price": 4500,
        "color": "#f59e0b",
        "rarity": "legendary"
    },

    {
        "id": "plasma",
        "name": "Плазма",
        "price": 5000,
        "color": "#d946ef",
        "rarity": "legendary"
    },

    {
        "id": "dark_matter",
        "name": "Тёмная материя",
        "price": 5500,
        "color": "#111827",
        "rarity": "legendary"
    },

    {
        "id": "crystal",
        "name": "Кристалл",
        "price": 6000,
        "color": "#22d3ee",
        "rarity": "legendary"
    },

    {
        "id": "lava",
        "name": "Лава",
        "price": 6500,
        "color": "#f43f5e",
        "rarity": "legendary"
    },

    {
        "id": "storm",
        "name": "Шторм",
        "price": 7000,
        "color": "#64748b",
        "rarity": "legendary"
    },

    {
        "id": "rainbow",
        "name": "Радуга",
        "price": 7500,
        "color": "#ec4899",
        "rarity": "legendary"
    },

    {
        "id": "ghost",
        "name": "Призрак",
        "price": 8000,
        "color": "#e2e8f0",
        "rarity": "legendary"
    },

    {
        "id": "radiation",
        "name": "Радиация",
        "price": 8500,
        "color": "#a3e635",
        "rarity": "legendary"
    },

    {
        "id": "arctic",
        "name": "Арктика",
        "price": 9000,
        "color": "#bae6fd",
        "rarity": "legendary"
    },

    {
        "id": "dragon",
        "name": "Дракон",
        "price": 10000,
        "color": "#7c3aed",
        "rarity": "mythic"
    },

    {
        "id": "royal",
        "name": "Королевский",
        "price": 12000,
        "color": "#eab308",
        "rarity": "mythic"
    },

    {
        "id": "diamond",
        "name": "Алмаз",
        "price": 15000,
        "color": "#60a5fa",
        "rarity": "mythic"
    },

    {
        "id": "star",
        "name": "Звезда",
        "price": 20000,
        "color": "#f8fafc",
        "rarity": "mythic"
    },

    {
        "id": "legendary_snake",
        "name": "Легендарная змея",
        "price": 30000,
        "color": "#facc15",
        "rarity": "mythic"
    }

]


RARITY_NAMES = {
    "common": "Обычный",
    "rare": "Редкий",
    "epic": "Эпический",
    "legendary": "Легендарный",
    "mythic": "Мифический"
}


# ============================================================
# ACHIEVEMENTS
# ============================================================

ACHIEVEMENTS = [

    {
        "id": "first_game",
        "name": "Первый шаг",
        "description": "Сыграть первую игру",
        "icon": "🐣",
        "reward": 50
    },

    {
        "id": "apple_master",
        "name": "Яблочный мастер",
        "description": "Набрать 10 очков",
        "icon": "🍎",
        "reward": 100
    },

    {
        "id": "warmed_up",
        "name": "Разогрелся",
        "description": "Набрать 25 очков",
        "icon": "🔥",
        "reward": 200
    },

    {
        "id": "legend",
        "name": "Легенда",
        "description": "Набрать 50 очков",
        "icon": "👑",
        "reward": 500
    },

    {
        "id": "gamer",
        "name": "Игроман",
        "description": "Сыграть 10 игр",
        "icon": "🎮",
        "reward": 250
    },

    {
        "id": "experienced",
        "name": "Опытный",
        "description": "Получить 1000 XP",
        "icon": "⭐",
        "reward": 500
    },

    {
        "id": "rich",
        "name": "Богач",
        "description": "Накопить 1000 монет",
        "icon": "💰",
        "reward": 500
    },

    {
        "id": "snake_master",
        "name": "Мастер змейки",
        "description": "Набрать 100 очков",
        "icon": "🐍",
        "reward": 1000
    },

    {
        "id": "treasure_hunter",
        "name": "Охотник за сокровищами",
        "description": "Открыть 10 сундуков",
        "icon": "🎁",
        "reward": 750
    }

]


# ============================================================
# DATABASE
# ============================================================

def get_db():

    connection = sqlite3.connect(
        DB_PATH,
        timeout=30
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_db():

    connection = get_db()
    cursor = connection.cursor()

    print("🔧 Проверка базы данных...")

    # ========================================================
    # PLAYERS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE NOT NULL,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            coins INTEGER DEFAULT 0,
            active_skin TEXT DEFAULT 'emerald',
            games_played INTEGER DEFAULT 0,
            best_score INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            daily_streak INTEGER DEFAULT 0,
            last_daily_reward TEXT DEFAULT '',
            chests_opened INTEGER DEFAULT 0,
            last_chest_opened TEXT DEFAULT '',
            total_coins_earned INTEGER DEFAULT 0
        )
    """)

    # ========================================================
    # MIGRATION PLAYERS
    # ========================================================

    cursor.execute(
        "PRAGMA table_info(players)"
    )

    player_columns = {
        row[1]
        for row in cursor.fetchall()
    }

    player_migrations = {

        "active_skin":
            "TEXT DEFAULT 'emerald'",

        "xp":
            "INTEGER DEFAULT 0",

        "level":
            "INTEGER DEFAULT 1",

        "daily_streak":
            "INTEGER DEFAULT 0",

        "last_daily_reward":
            "TEXT DEFAULT ''",

        "chests_opened":
            "INTEGER DEFAULT 0",

        "last_chest_opened":
            "TEXT DEFAULT ''",

        "total_coins_earned":
            "INTEGER DEFAULT 0"
    }

    for column, definition in player_migrations.items():

        if column not in player_columns:

            cursor.execute(
                f"""
                ALTER TABLE players
                ADD COLUMN {column} {definition}
                """
            )

            print(
                f"✓ Добавлена колонка players.{column}"
            )

    # ========================================================
    # ACHIEVEMENTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT NOT NULL,
            achievement_id TEXT NOT NULL,
            unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(telegram_id, achievement_id)
        )
    """)

    # ========================================================
    # SKINS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skins (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price INTEGER DEFAULT 0,
            color TEXT NOT NULL,
            rarity TEXT DEFAULT 'common'
        )
    """)

    # ========================================================
    # SKINS MIGRATION
    # ========================================================

    cursor.execute(
        "PRAGMA table_info(skins)"
    )

    skins_info = cursor.fetchall()

    skin_columns = {
        row[1]
        for row in skins_info
    }

    id_info = next(
        (
            row
            for row in skins_info
            if row[1] == "id"
        ),
        None
    )

    id_is_text = False

    if id_info:

        id_type = (
            id_info[2] or ""
        ).upper()

        id_is_text = (
            "TEXT" in id_type
        )

    # --------------------------------------------------------
    # Если старая skins имеет INTEGER id
    # --------------------------------------------------------

    if id_info and not id_is_text:

        print(
            "⚠ Обнаружена старая структура skins"
        )

        print(
            "🔧 Выполняется миграция skins..."
        )

        # ----------------------------------------------------
        # Создаём новую таблицу
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skins_new (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price INTEGER DEFAULT 0,
                color TEXT NOT NULL,
                rarity TEXT DEFAULT 'common'
            )
        """)

        old_skin_columns = set(
            skin_columns
        )

        # ----------------------------------------------------
        # Переносим старые скины
        # ----------------------------------------------------

        if {
            "id",
            "name",
            "price",
            "color"
        }.issubset(old_skin_columns):

            if "rarity" in old_skin_columns:

                cursor.execute("""
                    INSERT OR IGNORE INTO skins_new
                    (
                        id,
                        name,
                        price,
                        color,
                        rarity
                    )
                    SELECT
                        CAST(id AS TEXT),
                        COALESCE(name, ''),
                        COALESCE(price, 0),
                        COALESCE(color, '#22c55e'),
                        COALESCE(rarity, 'common')
                    FROM skins
                """)

            else:

                cursor.execute("""
                    INSERT OR IGNORE INTO skins_new
                    (
                        id,
                        name,
                        price,
                        color,
                        rarity
                    )
                    SELECT
                        CAST(id AS TEXT),
                        COALESCE(name, ''),
                        COALESCE(price, 0),
                        COALESCE(color, '#22c55e'),
                        'common'
                    FROM skins
                """)

        # ----------------------------------------------------
        # Сохраняем старую таблицу
        # ----------------------------------------------------

        cursor.execute("""
            ALTER TABLE skins
            RENAME TO skins_old
        """)

        # ----------------------------------------------------
        # Делаем новую таблицу основной
        # ----------------------------------------------------

        cursor.execute("""
            ALTER TABLE skins_new
            RENAME TO skins
        """)

        print(
            "✓ Таблица skins мигрирована"
        )

    else:

        # ----------------------------------------------------
        # Добавляем недостающие колонки
        # ----------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(skins)"
        )

        skin_columns = {
            row[1]
            for row in cursor.fetchall()
        }

        if "name" not in skin_columns:

            cursor.execute("""
                ALTER TABLE skins
                ADD COLUMN name TEXT DEFAULT ''
            """)

            print(
                "✓ Добавлена skins.name"
            )

        if "price" not in skin_columns:

            cursor.execute("""
                ALTER TABLE skins
                ADD COLUMN price INTEGER DEFAULT 0
            """)

            print(
                "✓ Добавлена skins.price"
            )

        if "color" not in skin_columns:

            cursor.execute("""
                ALTER TABLE skins
                ADD COLUMN color TEXT DEFAULT '#22c55e'
            """)

            print(
                "✓ Добавлена skins.color"
            )

        if "rarity" not in skin_columns:

            cursor.execute("""
                ALTER TABLE skins
                ADD COLUMN rarity TEXT DEFAULT 'common'
            """)

            print(
                "✓ Добавлена skins.rarity"
            )

    # ========================================================
    # PLAYER SKINS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_skins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT NOT NULL,
            skin_id TEXT NOT NULL,
            purchased_at TEXT,
            UNIQUE(telegram_id, skin_id)
        )
    """)

    # ========================================================
    # MIGRATION PLAYER SKINS
    # ========================================================

    cursor.execute(
        "PRAGMA table_info(player_skins)"
    )

    player_skin_info = cursor.fetchall()

    player_skin_columns = {
        row[1]
        for row in player_skin_info
    }

    if "purchased_at" not in player_skin_columns:

        cursor.execute("""
            ALTER TABLE player_skins
            ADD COLUMN purchased_at TEXT
        """)

        print(
            "✓ Добавлена player_skins.purchased_at"
        )

    # --------------------------------------------------------
    # Приводим старые skin_id к TEXT
    # --------------------------------------------------------

    try:

        cursor.execute("""
            UPDATE player_skins
            SET skin_id = CAST(skin_id AS TEXT)
            WHERE skin_id IS NOT NULL
        """)

    except sqlite3.Error:

        pass

    # ========================================================
    # INSERT / UPDATE SKINS
    # ========================================================

    for skin in COIN_SKINS:

        cursor.execute("""
            INSERT OR IGNORE INTO skins
            (
                id,
                name,
                price,
                color,
                rarity
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            skin["id"],
            skin["name"],
            skin["price"],
            skin["color"],
            skin["rarity"]
        ))

        cursor.execute("""
            UPDATE skins
            SET
                name = ?,
                price = ?,
                color = ?,
                rarity = ?
            WHERE id = ?
        """, (
            skin["name"],
            skin["price"],
            skin["color"],
            skin["rarity"],
            skin["id"]
        ))

    # ========================================================
    # EMERALD
    # ========================================================

    cursor.execute("""
        INSERT OR IGNORE INTO skins
        (
            id,
            name,
            price,
            color,
            rarity
        )
        VALUES
        (
            'emerald',
            'Изумруд',
            0,
            '#22c55e',
            'common'
        )
    """)

    # ========================================================
    # INDEXES
    # ========================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_achievements_telegram
        ON achievements(telegram_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_player_skins_telegram
        ON player_skins(telegram_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_players_telegram
        ON players(telegram_id)
    """)

    # ========================================================
    # SAVE
    # ========================================================

    connection.commit()
    connection.close()

    print("✓ База данных проверена")
    print("✓ Таблица players: OK")
    print("✓ Таблица achievements: OK")
    print("✓ Таблица skins: OK")
    print("✓ Таблица player_skins: OK")
    print("✓ Миграции: OK")


# ============================================================
# PLAYER
# ============================================================

def ensure_player(
    telegram_id,
    username="",
    first_name=""
):

    telegram_id = str(
        telegram_id
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM players
        WHERE telegram_id = ?
    """, (
        telegram_id,
    ))

    player = cursor.fetchone()

    if not player:

        cursor.execute("""
            INSERT INTO players (
                telegram_id,
                username,
                first_name,
                coins,
                active_skin,
                games_played,
                best_score,
                total_score,
                xp,
                level,
                daily_streak,
                last_daily_reward,
                chests_opened,
                last_chest_opened,
                total_coins_earned
            )
            VALUES (
                ?,
                ?,
                ?,
                0,
                'emerald',
                0,
                0,
                0,
                0,
                1,
                0,
                '',
                0,
                '',
                0
            )
        """, (
            telegram_id,
            username or "",
            first_name or ""
        ))

    else:

        cursor.execute("""
            UPDATE players
            SET
                username = ?,
                first_name = ?
            WHERE telegram_id = ?
        """, (
            username or player["username"] or "",
            first_name or player["first_name"] or "",
            telegram_id
        ))

    cursor.execute("""
        SELECT *
        FROM players
        WHERE telegram_id = ?
    """, (
        telegram_id,
    ))

    player = cursor.fetchone()

    cursor.execute("""
        INSERT OR IGNORE INTO player_skins
        (
            telegram_id,
            skin_id
        )
        VALUES (?, 'emerald')
    """, (
        telegram_id,
    ))

    connection.commit()
    connection.close()

    return dict(player)


def get_player(telegram_id):

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM players
        WHERE telegram_id = ?
    """, (
        str(telegram_id),
    ))

    player = cursor.fetchone()

    connection.close()

    if player:

        return dict(player)

    return None


# ============================================================
# XP
# ============================================================

def xp_for_level(level):

    if level <= 1:

        return 0

    total = 0

    for current_level in range(
        2,
        level + 1
    ):

        total += (
            100 +
            (current_level - 2) * 50
        )

    return total


def level_from_xp(xp):

    level = 1

    while xp >= xp_for_level(
        level + 1
    ):

        level += 1

        if level >= 100:

            break

    return level


# ============================================================
# ACHIEVEMENTS
# ============================================================

def check_achievements(
    telegram_id
):

    player = get_player(
        telegram_id
    )

    if not player:

        return []

    unlocked_now = []

    connection = get_db()
    cursor = connection.cursor()

    for achievement in ACHIEVEMENTS:

        achievement_id = achievement["id"]

        cursor.execute("""
            SELECT id
            FROM achievements
            WHERE telegram_id = ?
            AND achievement_id = ?
        """, (
            str(telegram_id),
            achievement_id
        ))

        if cursor.fetchone():

            continue

        unlocked = False

        if achievement_id == "first_game":

            unlocked = (
                player["games_played"] >= 1
            )

        elif achievement_id == "apple_master":

            unlocked = (
                player["best_score"] >= 10
            )

        elif achievement_id == "warmed_up":

            unlocked = (
                player["best_score"] >= 25
            )

        elif achievement_id == "legend":

            unlocked = (
                player["best_score"] >= 50
            )

        elif achievement_id == "gamer":

            unlocked = (
                player["games_played"] >= 10
            )

        elif achievement_id == "experienced":

            unlocked = (
                player["xp"] >= 1000
            )

        elif achievement_id == "rich":

            unlocked = (
                player["coins"] >= 1000
            )

        elif achievement_id == "snake_master":

            unlocked = (
                player["best_score"] >= 100
            )

        elif achievement_id == "treasure_hunter":

            unlocked = (
                player["chests_opened"] >= 10
            )

        if unlocked:

            cursor.execute("""
                INSERT OR IGNORE INTO achievements
                (
                    telegram_id,
                    achievement_id
                )
                VALUES (?, ?)
            """, (
                str(telegram_id),
                achievement_id
            ))

            cursor.execute("""
                UPDATE players
                SET
                    coins = coins + ?,
                    total_coins_earned =
                        total_coins_earned + ?
                WHERE telegram_id = ?
            """, (
                achievement["reward"],
                achievement["reward"],
                str(telegram_id)
            ))

            unlocked_now.append(
                achievement
            )

    connection.commit()
    connection.close()

    return unlocked_now


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    return send_from_directory(
        os.path.join(
            BASE_DIR,
            "static"
        ),
        "index.html"
    )


# ============================================================
# PLAYER API
# ============================================================

@app.route(
    "/api/player/<telegram_id>"
)
def api_player(telegram_id):

    player = get_player(
        telegram_id
    )

    if not player:

        player = ensure_player(
            telegram_id
        )

    return jsonify(player)


# ============================================================
# STATS
# ============================================================

@app.route(
    "/api/stats/<telegram_id>"
)
def api_stats(telegram_id):

    player = get_player(
        telegram_id
    )

    if not player:

        player = ensure_player(
            telegram_id
        )

    return jsonify({

        "telegram_id":
            player["telegram_id"],

        "coins":
            player["coins"],

        "xp":
            player["xp"],

        "level":
            player["level"],

        "games_played":
            player["games_played"],

        "best_score":
            player["best_score"],

        "total_score":
            player["total_score"],

        "chests_opened":
            player["chests_opened"],

        "total_coins_earned":
            player["total_coins_earned"],

        "active_skin":
            player["active_skin"]

    })


# ============================================================
# SCORE
# ============================================================

@app.route(
    "/api/score",
    methods=["POST"]
)
def api_score():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    telegram_id = str(
        data.get(
            "telegram_id",
            ""
        )
    )

    try:

        score = int(
            data.get(
                "score",
                0
            )
        )

    except (
        ValueError,
        TypeError
    ):

        score = 0

    if not telegram_id:

        return jsonify({
            "error":
                "telegram_id required"
        }), 400

    if score < 0:

        score = 0

    if score > 100000:

        score = 100000

    player = get_player(
        telegram_id
    )

    if not player:

        player = ensure_player(
            telegram_id
        )

    gained_xp = (
        score *
        XP_PER_FOOD
    )

    connection = get_db()
    cursor = connection.cursor()

    new_games = (
        player["games_played"] + 1
    )

    new_total_score = (
        player["total_score"] +
        score
    )

    new_best = max(
        player["best_score"],
        score
    )

    new_xp = (
        player["xp"] +
        gained_xp
    )

    new_level = level_from_xp(
        new_xp
    )

    cursor.execute("""
        UPDATE players
        SET
            games_played = ?,
            total_score = ?,
            best_score = ?,
            xp = ?,
            level = ?
        WHERE telegram_id = ?
    """, (
        new_games,
        new_total_score,
        new_best,
        new_xp,
        new_level,
        telegram_id
    ))

    connection.commit()
    connection.close()

    unlocked = check_achievements(
        telegram_id
    )

    updated_player = get_player(
        telegram_id
    )

    return jsonify({

        "success":
            True,

        "score":
            score,

        "xp_gained":
            gained_xp,

        "xp":
            updated_player["xp"],

        "level":
            updated_player["level"],

        "level_up":
            new_level >
            player["level"],

        "coins":
            updated_player["coins"],

        "best_score":
            updated_player["best_score"],

        "games_played":
            updated_player["games_played"],

        "unlocked_achievements":
            unlocked

    })


# ============================================================
# SKINS
# ============================================================

@app.route("/api/skins")
def api_skins():

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            price,
            color,
            rarity
        FROM skins
        ORDER BY price ASC
    """)

    skins = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return jsonify({
        "skins": skins
    })


# ============================================================
# MY SKINS
# ============================================================

@app.route(
    "/api/my-skins/<telegram_id>"
)
def api_my_skins(telegram_id):

    player = get_player(
        telegram_id
    )

    if not player:

        player = ensure_player(
            telegram_id
        )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT skin_id
        FROM player_skins
        WHERE telegram_id = ?
    """, (
        str(telegram_id),
    ))

    owned = [
        str(row["skin_id"])
        for row in cursor.fetchall()
    ]

    if "emerald" not in owned:

        owned.append(
            "emerald"
        )

        cursor.execute("""
            INSERT OR IGNORE INTO player_skins
            (
                telegram_id,
                skin_id
            )
            VALUES (?, 'emerald')
        """, (
            str(telegram_id),
        ))

        connection.commit()

    connection.close()

    return jsonify({

        "owned":
            owned,

        "active_skin":
            player["active_skin"]
            or "emerald"

    })


# ============================================================
# BUY SKIN
# ============================================================

@app.route(
    "/api/buy-skin",
    methods=["POST"]
)
def api_buy_skin():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    telegram_id = str(
        data.get(
            "telegram_id",
            ""
        )
    )

    skin_id = str(
        data.get(
            "skin_id",
            ""
        )
    )

    if not telegram_id or not skin_id:

        return jsonify({
            "error":
                "Не хватает данных"
        }), 400

    player = get_player(
        telegram_id
    )

    if not player:

        player = ensure_player(
            telegram_id
        )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM skins
        WHERE id = ?
    """, (
        skin_id,
    ))

    skin = cursor.fetchone()

    if not skin:

        connection.close()

        return jsonify({
            "error":
                "Скин не найден"
        }), 404

    cursor.execute("""
        SELECT id
        FROM player_skins
        WHERE telegram_id = ?
        AND skin_id = ?
    """, (
        telegram_id,
        skin_id
    ))

    if cursor.fetchone():

        connection.close()

        return jsonify({
            "error":
                "Скин уже куплен"
        }), 400

    price = int(
        skin["price"]
    )

    if price > player["coins"]:

        connection.close()

        return jsonify({
            "error":
                "Недостаточно монет"
        }), 400

    cursor.execute("""
        UPDATE players
        SET
            coins = coins - ?
        WHERE telegram_id = ?
    """, (
        price,
        telegram_id
    ))

    cursor.execute("""
        INSERT INTO player_skins
        (
            telegram_id,
            skin_id
        )
        VALUES (?, ?)
    """, (
        telegram_id,
        skin_id
    ))

    connection.commit()

    cursor.execute("""
        SELECT coins
        FROM players
        WHERE telegram_id = ?
    """, (
        telegram_id,
    ))

    coins = cursor.fetchone()["coins"]

    connection.close()

    return jsonify({

        "success":
            True,

        "coins":
            coins,

        "skin":
            dict(skin)

    })


# ============================================================
# EQUIP SKIN
# ============================================================

@app.route(
    "/api/equip-skin",
    methods=["POST"]
)
def api_equip_skin():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    telegram_id = str(
        data.get(
            "telegram_id",
            ""
        )
    )

    skin_id = str(
        data.get(
            "skin_id",
            ""
        )
    )

    if not telegram_id or not skin_id:

        return jsonify({
            "error":
                "Не хватает данных"
        }), 400

    player = get_player(
        telegram_id
    )

    if not player:

        return jsonify({
            "error":
                "Игрок не найден"
        }), 404

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM skins
        WHERE id = ?
    """, (
        skin_id,
    ))

    skin = cursor.fetchone()

    if not skin:

        connection.close()

        return jsonify({
            "error":
                "Скин не найден"
        }), 404

    if skin_id != "emerald":

        cursor.execute("""
            SELECT id
            FROM player_skins
            WHERE telegram_id = ?
            AND skin_id = ?
        """, (
            telegram_id,
            skin_id
        ))

        if not cursor.fetchone():

            connection.close()

            return jsonify({
                "error":
                    "Сначала купи этот скин"
            }), 400

    cursor.execute("""
        UPDATE players
        SET active_skin = ?
        WHERE telegram_id = ?
    """, (
        skin_id,
        telegram_id
    ))

    connection.commit()
    connection.close()

    return jsonify({

        "success":
            True,

        "active_skin":
            skin_id,

        "skin":
            dict(skin)

    })


# ============================================================
# DAILY REWARD
# ============================================================

@app.route(
    "/api/daily-reward",
    methods=["POST"]
)
def api_daily_reward():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    telegram_id = str(
        data.get(
            "telegram_id",
            ""
        )
    )

    if not telegram_id:

        return jsonify({
            "error":
                "telegram_id required"
        }), 400

    player = get_player(
        telegram_id
    )

    if not player:

        player = ensure_player(
            telegram_id
        )

    now = datetime.now()

    last_reward = None

    if player["last_daily_reward"]:

        try:

            last_reward = (
                datetime.fromisoformat(
                    player[
                        "last_daily_reward"
                    ]
                )
            )

        except ValueError:

            last_reward = None

    if last_reward:

        if (
            now - last_reward
            <
            timedelta(days=1)
        ):

            next_time = (
                last_reward +
                timedelta(days=1)
            )

            seconds = max(
                0,
                int(
                    (
                        next_time -
                        now
                    ).total_seconds()
                )
            )

            return jsonify({

                "success":
                    False,

                "available":
                    False,

                "seconds_left":
                    seconds,

                "streak":
                    player[
                        "daily_streak"
                    ]

            })

    streak = (
        player["daily_streak"] +
        1
    )

    if streak > len(
        DAILY_REWARDS
    ):

        streak = 1

    reward = DAILY_REWARDS[
        streak - 1
    ]

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE players
        SET
            coins = coins + ?,
            daily_streak = ?,
            last_daily_reward = ?,
            total_coins_earned =
                total_coins_earned + ?
        WHERE telegram_id = ?
    """, (
        reward,
        streak,
        now.isoformat(),
        reward,
        telegram_id
    ))

    connection.commit()
    connection.close()

    check_achievements(
        telegram_id
    )

    return jsonify({

        "success":
            True,

        "available":
            False,

        "reward":
            reward,

        "coins":
            reward,

        "streak":
            streak

    })


# ============================================================
# CHEST STATUS
# ============================================================

@app.route(
    "/api/chest",
    methods=["GET"]
)
def api_chest_status():

    telegram_id = str(
        request.args.get(
            "telegram_id",
            ""
        )
    )

    if not telegram_id:

        return jsonify({
            "error":
                "telegram_id required"
        }), 400

    player = get_player(
        telegram_id
    )

    if not player:

        player = ensure_player(
            telegram_id
        )

    now = datetime.now()

    available = True
    seconds_left = 0

    if player["last_chest_opened"]:

        try:

            last_opened = (
                datetime.fromisoformat(
                    player[
                        "last_chest_opened"
                    ]
                )
            )

            next_open = (
                last_opened +
                timedelta(
                    hours=
                    CHEST_COOLDOWN_HOURS
                )
            )

            if now < next_open:

                available = False

                seconds_left = max(
                    0,
                    int(
                        (
                            next_open -
                            now
                        ).total_seconds()
                    )
                )

        except ValueError:

            pass

    return jsonify({

        "available":
            available,

        "seconds_left":
            seconds_left,

        "chests_opened":
            player[
                "chests_opened"
            ]

    })


# ============================================================
# OPEN CHEST
# ============================================================

@app.route(
    "/api/chest",
    methods=["POST"]
)
def api_open_chest():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    telegram_id = str(
        data.get(
            "telegram_id",
            ""
        )
    )

    if not telegram_id:

        return jsonify({
            "error":
                "telegram_id required"
        }), 400

    player = get_player(
        telegram_id
    )

    if not player:

        player = ensure_player(
            telegram_id
        )

    now = datetime.now()

    if player["last_chest_opened"]:

        try:

            last_opened = (
                datetime.fromisoformat(
                    player[
                        "last_chest_opened"
                    ]
                )
            )

            if (
                now - last_opened
                <
                timedelta(
                    hours=
                    CHEST_COOLDOWN_HOURS
                )
            ):

                next_open = (
                    last_opened +
                    timedelta(
                        hours=
                        CHEST_COOLDOWN_HOURS
                    )
                )

                seconds_left = max(
                    0,
                    int(
                        (
                            next_open -
                            now
                        ).total_seconds()
                    )
                )

                return jsonify({

                    "success":
                        False,

                    "available":
                        False,

                    "seconds_left":
                        seconds_left

                })

        except ValueError:

            pass

    roll = random.random()

    reward_type = "coins"
    reward = 0

    if roll < 0.60:

        reward = random.randint(
            100,
            250
        )

        reward_type = "coins"

    elif roll < 0.85:

        reward = random.randint(
            250,
            500
        )

        reward_type = "coins"

    elif roll < 0.95:

        reward = random.randint(
            20,
            60
        )

        reward_type = "xp"

    else:

        reward = 1000

        reward_type = "jackpot"

    connection = get_db()
    cursor = connection.cursor()

    if reward_type in (
        "coins",
        "jackpot"
    ):

        cursor.execute("""
            UPDATE players
            SET
                coins = coins + ?,
                chests_opened =
                    chests_opened + 1,
                last_chest_opened = ?,
                total_coins_earned =
                    total_coins_earned + ?
            WHERE telegram_id = ?
        """, (
            reward,
            now.isoformat(),
            reward,
            telegram_id
        ))

    else:

        cursor.execute("""
            UPDATE players
            SET
                xp = xp + ?,
                chests_opened =
                    chests_opened + 1,
                last_chest_opened = ?
            WHERE telegram_id = ?
        """, (
            reward,
            now.isoformat(),
            telegram_id
        ))

    connection.commit()
    connection.close()

    updated_player = get_player(
        telegram_id
    )

    new_level = level_from_xp(
        updated_player["xp"]
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE players
        SET level = ?
        WHERE telegram_id = ?
    """, (
        new_level,
        telegram_id
    ))

    connection.commit()
    connection.close()

    unlocked = check_achievements(
        telegram_id
    )

    final_player = get_player(
        telegram_id
    )

    return jsonify({

        "success":
            True,

        "available":
            False,

        "reward":
            reward,

        "reward_type":
            reward_type,

        "xp":
            final_player["xp"],

        "coins":
            final_player["coins"],

        "level":
            final_player["level"],

        "unlocked_achievements":
            unlocked

    })


# ============================================================
# LEADERBOARD
# ============================================================

@app.route(
    "/api/leaderboard"
)
def api_leaderboard():

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            telegram_id,
            username,
            first_name,
            best_score,
            total_score,
            games_played,
            level
        FROM players
        ORDER BY
            best_score DESC,
            total_score DESC
        LIMIT 100
    """)

    rows = cursor.fetchall()

    connection.close()

    leaderboard = []

    for index, row in enumerate(rows):

        name = (
            row["username"]
            or row["first_name"]
            or "Игрок"
        )

        leaderboard.append({

            "rank":
                index + 1,

            "telegram_id":
                row["telegram_id"],

            "username":
                name,

            "name":
                name,

            "best_score":
                row["best_score"],

            "score":
                row["best_score"],

            "total_score":
                row["total_score"],

            "games_played":
                row["games_played"],

            "level":
                row["level"]

        })

    return jsonify({
        "leaderboard":
            leaderboard
    })


@app.route(
    "/api/rating"
)
def api_rating():

    return api_leaderboard()


# ============================================================
# ACHIEVEMENTS API
# ============================================================

@app.route(
    "/api/achievements/<telegram_id>"
)
def api_achievements(telegram_id):

    player = get_player(
        telegram_id
    )

    if not player:

        player = ensure_player(
            telegram_id
        )

    check_achievements(
        telegram_id
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT achievement_id
        FROM achievements
        WHERE telegram_id = ?
    """, (
        str(telegram_id),
    ))

    unlocked_ids = {
        row["achievement_id"]
        for row in cursor.fetchall()
    }

    connection.close()

    result = []

    for achievement in ACHIEVEMENTS:

        item = {
            **achievement,
            "unlocked":
                achievement["id"]
                in unlocked_ids
        }

        result.append(item)

    return jsonify({
        "achievements":
            result
    })


# ============================================================
# FLASK RUNNER
# ============================================================

def run_flask():

  app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    debug=False,
    use_reloader=False
)


# ============================================================
# TELEGRAM BOT
# ============================================================

dp = Dispatcher()


@dp.message(
    CommandStart()
)
async def command_start(
    message: types.Message
):

    if not BOT_TOKEN:

        return

    user = message.from_user

    ensure_player(
        user.id,
        user.username or "",
        user.first_name or ""
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🐍 Играть",
                    web_app=WebAppInfo(
                        url=WEB_APP_URL
                    )
                )
            ]
        ]
    )

    await message.answer(

        "🐍 <b>Snake Legends</b>\n\n"
        "Собирай яблоки, получай XP, "
        "зарабатывай монеты и открывай "
        "новые скины!\n\n"
        "Готов начать?",

        reply_markup=keyboard,

        parse_mode="HTML"
    )


async def run_bot():

    if not BOT_TOKEN:

        print(
            "ОШИБКА: BOT_TOKEN не найден в .env"
        )

        return

    bot = Bot(
        token=BOT_TOKEN
    )

    print(
        "Telegram bot запущен."
    )

    await dp.start_polling(
        bot
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 50)
    print("🐍 SNAKE LEGENDS")
    print("=" * 50)

    init_db()

    print(
        "Flask: http://127.0.0.1:5000"
    )

    print(
        f"WebApp: {WEB_APP_URL}"
    )

    print("=" * 50)
    print()

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    try:

        asyncio.run(
            run_bot()
        )

    except KeyboardInterrupt:

        print(
            "\nБот остановлен."
        )
