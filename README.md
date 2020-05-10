# Roll-Bot

A tabletop dice rolling bot, which can easily be deployed to Heroku.

## Configuration

The config files contain four possible entries at the moment. By default local running will use the `config/local.json` file and production will use `config/production.json`. Two example json files are provided which you can rename. The local config is gitignored to avoid exposing your testing discord bot token. It is recommended you use [Heroku environment variables](https://devcenter.heroku.com/articles/config-vars) for production configuration.

Entries `discord_token` or `discord_token_env_var` are used to set your discord bot token. If the first one is set the second one is ignored. The first one is used to directly set the token, while the second one can be used to set the name of an environment variable that holds the token.

The same principle applies for `redis_url` and `redis_url_env_var`. Note that if neither is set the app will still run without variable environment saving.

## Running Locally

Make sure you have Python 3.8.2 installed locally, for example using [pyenv](https://github.com/pyenv/pyenv-installer) (be sure to check the [Common build problems](https://github.com/pyenv/pyenv/wiki/common-build-problems) page if you run into any issues). To push to Heroku, you'll need to install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli). Additionally, to make user variable environments you'll need to setup redis. I suggest you don't bother with this for your local testing setup. I use [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) to manage dependencies. For just running it you can also revert back to plain pip though.

```sh
$ git clone https://github.com/thijsmie/roll-bot.git
$ cd roll-bot-standalone

# raw installing dependencies
$ python3 -m venv roll-bot-standalone
$ source roll-bot-standalone/bin/activate
$ pip install -r requirements.txt

# pyenv installing dependencies
$ pyenv install 3.8.2
$ pyenv shell 3.8.2
$ pyenv virtualenv roll-bot-standalone
$ pyenv activate roll-bot-standalone
$ pip install -r requirements.txt

# pyenv+pipenv installing dependencies
$ pyenv install 3.8.2
$ pyenv shell 3.8.2
$ pip install pipenv
$ pipenv install

# raw running the app
$ source roll-bot-standalone/bin/activate
$ python runlocal.py

# pyenv running the app
$ pyenv activate roll-bot-standalone
$ python runlocal.py

# pyenv+pipenv running the app
$ pipenv run python runlocal.py
```

Your app should now be running and announce its discord username.

## Deploying to Heroku

First create a new app on heroku, using free dynos is fine. Provision the [RedisCloud](https://elements.heroku.com/addons/rediscloud) addon, again, free tier is fine. Now set an environment variable DISCORD_TOKEN with your discord bot token and copy `production.example.json` to `production.json`.

Then in the terminal run the following commands.

```sh
$ heroku git:remote -a HerokuAppName 
$ git push heroku master
```

Your app should now be live.