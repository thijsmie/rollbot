import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from rollbot.bot.handlers import roll as roll_handler


def test_bot_importable():
    # Best we can do, we'll test the handlers separately.
    pass


def _make_context():
    context = MagicMock()
    context.user.id = "123"
    context.guild_id = "456"
    context.followup.send = AsyncMock()
    return context


def test_roll_timeout():
    context = _make_context()

    with patch("rollbot.bot.handlers.asyncio.wait_for", side_effect=asyncio.TimeoutError):
        asyncio.run(roll_handler(context, "1000000d1"))

    context.followup.send.assert_awaited_once()
    sent = context.followup.send.call_args[0][0]
    assert "timed out" in sent.lower()
