from __future__ import annotations

import discord


class NextButton(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="<:right:878668370331983913>", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if self.view.current_page < len(self.view.records):
            self.view.current_page += 1
            await self.view.refresh_view()


class PrevButton(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="<:left:878668491660623872>", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if self.view.current_page > 1:
            self.view.current_page -= 1
            await self.view.refresh_view()


class StopButton(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="<:stop:878668481828343838>", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.view.on_timeout()
        self.view.stop()
