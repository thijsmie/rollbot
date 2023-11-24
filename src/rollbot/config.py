import logging
import json
import os

from .db import make_db
from .varenv import var_env_provider


class Config:
    def __init__(self, config: str | dict[str, str]):
        if isinstance(config, str):
            with open(config) as f:
                config = json.load(f)

        if "discord_token" in config:
            self.token = config["discord_token"]
        elif "discord_token_env_var" in config:
            self.token = os.environ[config["discord_token_env_var"]]
        else:
            logging.error("Config could not aquire a discord token!")
            self.token = ""

        if "redis_url" in config:
            self.db = make_db(config["redis_url"])
        elif "redis_url_env_var" in config:
            self.db = make_db(os.environ[config["redis_url_env_var"]])
        else:
            self.db = None

        var_env_provider.set_db(self.db)
