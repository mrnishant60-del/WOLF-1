from __future__ import annotations

import discord

__all__ = ("IdpView",)


class IdpView(discord.ui.View):
    def __init__(self, room_id: str, password: str, map: str, youtube_link: str = None):
        self.room_id = room_id
        self.password = password
        self.map = map
        self.youtube_link = youtube_link
        super().__init__(timeout=None)

    @discord.ui.button(label="Get in Copy Format", style=discord.ButtonStyle.green)
    async def copy_format(self, interaction: discord.Interaction, button: discord.Button):
        message = "ID: {}\nPassword: {}\nMap: {}".format(self.room_id, self.password, self.map)
        if self.youtube_link:
            message += f"\nYouTube: {self.youtube_link}"
        await interaction.response.send_message(message, ephemeral=True)
