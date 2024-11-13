import io

import pytest

from rollbot.db import SQLiteDB
from rollbot.interpreter.calculator import evaluate
from rollbot.plottenbakker.plotter import plot_statistics
from rollbot.stat_tracker import stat_tracker
from rollbot.varenv import var_env_provider


@pytest.fixture(scope="function")
def db():
    db = SQLiteDB(":memory:")
    var_env_provider.set_db(db)
    stat_tracker.set_db(db)
    yield db
    db.close()
    stat_tracker.set_db(None)
    var_env_provider.set_db(None)


def test_var_env(db):
    env = var_env_provider.get("name", "user", "guild")
    env.set("key", "d100")
    env.set("key2", "d20")
    var_env_provider.update(env)
    evaluated = evaluate("key", env)

    assert "key" in evaluated
    assert "d100" in evaluated


def test_stat_tracker(db):
    env = var_env_provider.get("name", "user", "guild")

    evaluate("d20", env)

    stats = stat_tracker.get_user_stats("user", 20, 1)
    assert len(stats) == 1
    assert 1 <= next(iter(stats.keys())) <= 20
    assert next(iter(stats.values())) == 1

    stats = stat_tracker.get_guild_stats("guild", 20, 1)
    assert len(stats) == 1
    assert 1 <= next(iter(stats.keys())) <= 20
    assert next(iter(stats.values())) == 1

    stats = stat_tracker.get_global_stats(20, 1)
    assert len(stats) == 1
    assert 1 <= next(iter(stats.keys())) <= 20
    assert next(iter(stats.values())) == 1


def test_stat_tracker_plotting(db):
    for i in range(1, 21):
        for _ in range(i + 2):
            stat_tracker.increment_stat("guild", "user", 20, i)

    stats = stat_tracker.get_user_stats("user", 20, 1)

    output = io.BytesIO()
    plot_statistics(output, "Stats of user with a d20 today", stats, 20)

    assert output.getvalue().startswith(b"\x89PNG")
