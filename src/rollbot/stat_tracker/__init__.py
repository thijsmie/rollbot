import sqlite3
from collections import defaultdict
from datetime import datetime

from rollbot.db import SQLiteDB


class StatTracker:
    def __init__(self):
        self.db: SQLiteDB | None = None
        self.conn: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    def set_db(self, db: SQLiteDB | None) -> None:
        self.db = db
        if self.db is not None:
            self.conn = self.db.conn
            self.cursor = self.db.cursor
        else:
            self.conn = None
            self.cursor = None

    def increment_stat(self, guild: str, user: str, die: int, value: int) -> None:
        if not self.db:
            return

        day = datetime.now().date().toordinal()

        self.cursor.execute(
            """
            INSERT INTO die_stats (day, user_or_guild, die, result, count)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT (day, user_or_guild, die, result)
            DO UPDATE SET count = count + 1
        """,
            (day, f"@user-{user}", die, value),
        )
        # Also update the guild stats
        self.cursor.execute(
            """
            INSERT INTO die_stats (day, user_or_guild, die, result, count)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT (day, user_or_guild, die, result)
            DO UPDATE SET count = count + 1
        """,
            (day, f"@guild-{guild}", die, value),
        )
        # And global stats
        self.cursor.execute(
            """
            INSERT INTO die_stats (day, user_or_guild, die, result, count)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT (day, user_or_guild, die, result)
            DO UPDATE SET count = count + 1
        """,
            (day, "@global", die, value),
        )

        self.conn.commit()

    def get_user_stats(self, user: str, die: int, days: int) -> dict[int, int]:
        day = datetime.now().date().toordinal()
        self.cursor.execute(
            """
            SELECT result, count
            FROM die_stats
            WHERE user_or_guild = ? AND die = ? AND day >= ?
        """,
            (f"@user-{user}", die, day - days),
        )
        res = defaultdict(int)
        for row in self.cursor.fetchall():
            res[row[0]] += row[1]

        return dict(res)

    def get_guild_stats(self, guild: str, die: int, days: int) -> dict[int, int]:
        day = datetime.now().date().toordinal()
        self.cursor.execute(
            """
            SELECT result, count
            FROM die_stats
            WHERE user_or_guild = ? AND die = ? AND day >= ?
        """,
            (f"@guild-{guild}", die, day - days),
        )
        res = defaultdict(int)
        for row in self.cursor.fetchall():
            res[row[0]] += row[1]

        return dict(res)

    def get_global_stats(self, die: int, days: int) -> dict[int, int]:
        day = datetime.now().date().toordinal()
        self.cursor.execute(
            """
            SELECT result, count
            FROM die_stats
            WHERE user_or_guild = ? AND die = ? AND day >= ?
        """,
            ("@global", die, day - days),
        )
        res = defaultdict(int)
        for row in self.cursor.fetchall():
            res[row[0]] += row[1]

        return dict(res)

    def get_user_stats_overall(self, user: str, die: int) -> dict[int, int]:
        self.cursor.execute(
            """
            SELECT result, count
            FROM die_stats
            WHERE user_or_guild = ? AND die = ?
        """,
            (f"@user-{user}", die),
        )
        res = defaultdict(int)
        for row in self.cursor.fetchall():
            res[row[0]] += row[1]

        return dict(res)

    def get_guild_stats_overall(self, guild: str, die: int) -> dict[int, int]:
        self.cursor.execute(
            """
            SELECT result, count
            FROM die_stats
            WHERE user_or_guild = ? AND die = ?
        """,
            (f"@guild-{guild}", die),
        )
        res = defaultdict(int)
        for row in self.cursor.fetchall():
            res[row[0]] += row[1]

        return dict(res)

    def get_global_stats_overall(self, die: int) -> dict[int, int]:
        self.cursor.execute(
            """
            SELECT result, count
            FROM die_stats
            WHERE user_or_guild = ? AND die = ?
        """,
            ("@global", die),
        )
        res = defaultdict(int)
        for row in self.cursor.fetchall():
            res[row[0]] += row[1]

        return dict(res)


stat_tracker = StatTracker()
