import sys
import os
sys.path.insert(0, os.getcwd())

from rollbot.bot import client, envs
from rollbot.config import Config

config = Config("config/local.json")

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

envs.set_db(config.db)
client.run(config.token)