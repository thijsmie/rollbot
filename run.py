import asyncio  
import logging

from rollbot.bot import client, envs
from rollbot.config import Config

config = Config("config/production.json")

logging.basicConfig(
    level=logging.WARNING,
    # Not printing the time here, since Heroku already adds the time to the logs.
    format="%(levelname)s: %(message)s", 
    datefmt="%H:%M:%S",
)

envs.set_db(config.db)
client.run(config.token)