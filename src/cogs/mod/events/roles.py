from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from core import Wolf

from core import Cog


class RoleEvents(Cog):
    def __init__(self, bot: Wolf):
        self.bot = bot
