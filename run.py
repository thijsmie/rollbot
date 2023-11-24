import logging
import sys
from pathlib import Path

sys.path.insert(0, str((Path(__file__).parent / 'src').resolve()))

from rollbot.bot import bot
from rollbot.config import Config


config = Config("config/production.json")

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
)

bot.run(config.token)
