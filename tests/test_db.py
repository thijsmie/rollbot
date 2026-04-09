import io

import pytest

from rollbot.db import SQLiteDB
from rollbot.interpreter.calculator import evaluate
from rollbot.plottenbakker.plotter import plot_statistics
from rollbot.stat_tracker import stat_tracker
from rollbot.varenv import VarEnv, var_env_provider


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


def test_stat_tracker_overall(db):
    stat_tracker.increment_stat("guild", "user", 6, 3)
    stat_tracker.increment_stat("guild", "user", 6, 3)
    stat_tracker.increment_stat("guild", "user", 6, 5)

    stats = stat_tracker.get_user_stats_overall("user", 6)
    assert stats[3] == 2
    assert stats[5] == 1

    stats = stat_tracker.get_guild_stats_overall("guild", 6)
    assert stats[3] == 2
    assert stats[5] == 1

    stats = stat_tracker.get_global_stats_overall(6)
    assert stats[3] == 2
    assert stats[5] == 1


def test_varenv_unset(db):
    env = var_env_provider.get("name", "user", "guild")
    env.set("x", "5")
    assert env.get("x") == "5"

    # Unset a key that is present
    env.unset("x")
    assert env.get("x") is None
    assert env.dirty

    # Unset a key that is absent — no-op, dirty stays as-is
    env2 = var_env_provider.get("name2", "user", "guild")
    env2.unset("missing")
    assert not env2.dirty


def test_varenv_set_nonstr_key():
    env = VarEnv("test", "test", "test")
    with pytest.raises(Exception, match="NONSTR"):
        env.set(123, "value")


def test_varenv_provider_no_db():
    # var_env_provider.db is None here (no db fixture)
    env = var_env_provider.get("ghost", "user", "guild")
    assert env.name == "ghost"
    assert env.items == {}


def test_varenv_provider_data_retrieved(db):
    # Store items, then retrieve the same env name to cover the "data found" path
    env = var_env_provider.get("user1", "user1", "guild")
    env.set("roll", "d20")
    var_env_provider.update(env)

    env2 = var_env_provider.get("user1", "user1", "guild")
    assert env2.items == {"roll": "d20"}


def test_varenv_update_not_dirty(db):
    # Covers the update() branch where dirty=False — should be a no-op
    env = var_env_provider.get("name", "user", "guild")
    assert not env.dirty
    var_env_provider.update(env)

    # Still no data in db
    env2 = var_env_provider.get("name", "user", "guild")
    assert env2.items == {}
