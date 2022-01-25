import os
import sys
import logging
sys.path.insert(0, os.getcwd())

from rollbot.bot import bot
from rollbot.config import Config


config = Config("config/local.json")

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

bot.run(config.token)
