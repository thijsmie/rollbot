import logging
import dotenv

from rollbot.bot import bot
from rollbot.db import SQLiteDB
from rollbot.varenv import var_env_provider


config = dotenv.dotenv_values("env")


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
)
token = config["DISCORD_TOKEN"]
db = SQLiteDB(config["SQLITE_PATH"])
var_env_provider.set_db(db)

bot.run(token)
db.close()
