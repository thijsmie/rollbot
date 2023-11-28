import logging
import os

from rollbot.bot import bot
from rollbot.db import SQLiteDB
from rollbot.varenv import var_env_provider


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
)
token = os.environ["DISCORD_TOKEN"]
db = SQLiteDB(os.environ["SQLITE_PATH"])
var_env_provider.set_db(db)

bot.run(token)
db.close()
