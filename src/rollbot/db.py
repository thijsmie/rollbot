import json
import sqlite3


class SQLiteDB:
    def __init__(self, database_url: str):
        self.conn = sqlite3.connect(database_url)
        self.cursor = self.conn.cursor()

        # Create a table for key-value pairs if it doesn't exist
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS key_value (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS die_stats (
                day INTEGER NOT NULL,
                user_or_guild TEXT NOT NULL,
                die INTEGER NOT NULL,
                result INTEGER NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (day, user_or_guild, die, result)
            )
            """
        )
        self.conn.commit()

    def get(self, key: str) -> dict[str, str]:
        self.cursor.execute("SELECT value FROM key_value WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        if result is not None:
            return json.loads(result[0])
        else:
            return {}

    def set(self, key: str, value: dict[str, str]) -> None:
        serialized_value = json.dumps(value)
        self.cursor.execute(
            "INSERT OR REPLACE INTO key_value (key, value) VALUES (?, ?)",
            (key, serialized_value),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
