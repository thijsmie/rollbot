import os

import dotenv

from rollbot.bot import bot
from rollbot.db import SQLiteDB
from rollbot.logsetup import setup_logging
from rollbot.varenv import var_env_provider

config = dotenv.dotenv_values(os.environ.get("ROLLBOT_CONFIG_FILE", "/etc/data/env"))

setup_logging()

token = config["DISCORD_TOKEN"]
db = SQLiteDB(config["SQLITE_PATH"])
var_env_provider.set_db(db)

bot.run(token, log_handler=None)
db.close()
