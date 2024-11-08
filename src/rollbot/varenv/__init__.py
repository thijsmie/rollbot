from rollbot.db import SQLiteDB


class VarEnv:
    def __init__(self, name: str, items: dict[str, str] | None = None) -> None:
        self.dirty = False
        self.name = name
        self.items = items or {}

    def set(self, key: str, value: str) -> None:
        if not isinstance(key, str):
            raise Exception("ENV SET WITH KEY NONSTR")

        self.items[key] = value
        self.dirty = True

    def get(self, key: str) -> str | None:
        return self.items.get(key)


class VarEnvProvider:
    def __init__(self):
        self.db: SQLiteDB | None = None

    def set_db(self, db):
        self.db = db

    def get(self, name: str) -> VarEnv:
        if not self.db:
            return VarEnv(name)
        data = self.db.get(name)
        if not data:
            return VarEnv(name)
        return VarEnv(name, data)

    def update(self, varenv: VarEnv) -> None:
        if varenv.dirty and self.db is not None:
            self.db.set(varenv.name, varenv.items)


var_env_provider = VarEnvProvider()
