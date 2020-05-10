# Snippit to allow rollbot import from here
import sys
import os
sys.path.insert(0, os.getcwd())

from rollbot.bot import client, envs
from rollbot.config import Config

config = Config("config/production.json")

envs.set_db(config.db)
client.run(config.token)