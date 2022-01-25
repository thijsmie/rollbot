from typing import Optional, Dict, Any
import json


class VarEnv:
    def __init__(self, name: str, items: Dict[str, str] = None):
        self.dirty = False
        self.name = name
        self.items = items or {}

    def set(self, key: str, value: str) -> None:
        if type(key) != str:
            raise Exception("ENV SET WITH KEY NONSTR")

        self.items[key] = value
        self.dirty = True

    def get(self, key: str) -> Optional[str]:
        return self.items.get(key)


class VarEnvProvider:
    def __init__(self):
        self.db: Any = None

    def set_db(self, db):
        self.db = db

    def get(self, name: str) -> VarEnv:
        if not self.db:
            return VarEnv(name)
        return VarEnv(name, self.db.get(f"VarEnv[{name}]") or {})

    def update(self, varenv: VarEnv):
        if varenv.dirty and self.db is not None:
            self.db.set(f"VarEnv[{varenv.name}]", json.dumps(varenv.items))


var_env_provider = VarEnvProvider()
