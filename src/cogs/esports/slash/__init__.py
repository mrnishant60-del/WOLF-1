from __future__ import annotations

import typing as T

if T.TYPE_CHECKING:
    from core import Wolf

from core import Cog

from .scrims import *

__all__ = ("SlashCog",)


class SlashCog(Cog):
    def __init__(self, bot: Wolf):
        self.bot = bot

    async def cog_load(self) -> None:
        await self.bot.add_cog(ScrimsSlash(self.bot))


async def setup(bot: Wolf):
    await bot.add_cog(SlashCog(bot))
