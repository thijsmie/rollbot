import logging

from rollbot.bot import bot
from rollbot.config import Config


config = Config("config/production.json")

logging.basicConfig(
    level=logging.WARNING,
    format="[%(levelname)s] %(asctime)s - %(message)s",
)

bot.run(config.token)
