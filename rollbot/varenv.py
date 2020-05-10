import pickle
from redis import RedisError


class VarEnv:
    def __init__(self, name, db):
        self.name = name
        self.items = {}
        self.db = db

        try:
            f = db.get(name)
            data = pickle.loads(f)
            for k, v in data.items():
                self.items[k] = v
        except (AttributeError, RedisError):
            pass

    def set(self, key, value):
        self.items[key] = value
        try:
            self.db.set(self.name, pickle.dumps(self.items))
        except (AttributeError, RedisError):
            pass

    def get(self, key):
        return self.items[key]


class VarEnvProvider(object):
    def __init__(self):
        self.envs = {}
        self.db = None

    def set_db(self, db):
        self.db = db

    def get(self, name):
        if name not in self.envs:
            self.envs[name] = VarEnv(name, self.db)
        return self.envs[name]
