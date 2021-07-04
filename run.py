import asyncio  
import logging

from rollbot.bot import client, envs
from rollbot.config import Config

config = Config("config/production.json")

logging.basicConfig(
    level=logging.WARNING,
    format="[%(levelname)s] %(asctime)s - %(message)s", 
)

envs.set_db(config.db)
client.run(config.token)