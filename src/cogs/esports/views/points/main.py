from __future__ import annotations

import typing as T
from contextlib import suppress

import discord

from core import Context, WolfView
from utils import emote

from .conts import Team


class PointsTable(WolfView):
    def __init__(self, ctx: Context):
        super().__init__(ctx, timeout=100)

        self.teams: T.List[Team] = []
        self.header: T.Optional[str] = None
        self.footer: T.Optional[str] = None
        self.custom_id: T.Optional[T.List[str]] = None

    @property
    def initial_msg(self):
        _e = discord.Embed(color=self.bot.color, title="Points Table Maker")
        _e.description = "S.No. " + "Team Name".ljust(20) + "PP".ljust(4) + "Kills".ljust(6) + "SD".ljust(4) + "Total\n" "```\n"
        for idx, team in enumerate(self.teams, 1):
            sd_indicator = "💎" if team.super_duper > 0 else "-"
            _e.description += (
                f"{idx:02}. {team.name.ljust(20)} {str(team.placepts).ljust(4)} {str(team.kills).ljust(6)}"
                f"{sd_indicator.ljust(4)}{str(team.totalpts)}\n"
            )

        _e.description += "```"
        _e.set_footer(text=f"Header: {self.header or 'Not Set'}\nFooter: {self.footer or 'Not Set'}")
        
        if self.teams and any(t.logo for t in self.teams):
            first_team_with_logo = next((t for t in self.teams if t.logo), None)
            if first_team_with_logo:
                _e.set_thumbnail(url=first_team_with_logo.logo)
        
        return _e

    async def refresh_view(self):
        self.message = await self.message.edit(embed=self.initial_msg, view=self)

    @discord.ui.button(label="Title & Footer")
    async def set_title(self, inter: discord.Interaction, btn: discord.Button):
        modal = HeaderInput()
        await inter.response.send_modal(modal)
        await modal.wait()

        self.header = modal.header.value
        self.footer = modal.footer.value

        await self.refresh_view()

    @discord.ui.button(label="Add Team")
    async def add_team(self, inter: discord.Interaction, btn: discord.Button):
        modal = TeamInput()
        await inter.response.send_modal(modal)
        await modal.wait()

        kills, placepts, sd = None, None, 0

        with suppress(ValueError):
            kills = int(modal.kills.value)
            placepts = int(modal.placepts.value)
            if modal.super_duper.value:
                sd = int(modal.super_duper.value)

        if kills is None or placepts is None:
            return await self.ctx.error("Invalid input for kills or placement points.")

        team_name = modal.team_name.value
        logo = modal.logo_url.value if modal.logo_url.value else ""

        self.teams.append(
            Team(
                name=team_name,
                matches="1",
                kills=kills,
                placepts=placepts,
                totalpts=kills + placepts,
                logo=logo,
                super_duper=sd,
            )
        )
        await self.refresh_view()

    @discord.ui.button(label="Remove Team")
    async def remove_team(self, inter: discord.Interaction, btn: discord.Button):
        await inter.response.defer()
        if not self.teams:
            return await self.ctx.error("No teams to remove.")

        v = WolfView(self.ctx)
        v.add_item(TeamSelector(self.teams))
        msg = await inter.followup.send("", view=v, ephemeral=True)
        v.message = msg
        await v.wait()

        if not v.custom_id:
            return

        selected_ids = set(v.custom_id)
        self.teams = [team for team in self.teams if str(team.id) not in selected_ids]

        await self.refresh_view()

    @discord.ui.button(label="Send Table", style=discord.ButtonStyle.primary)
    async def send_table(self, inter: discord.Interaction, btn: discord.Button):
        if not inter.guild:
            return await inter.response.send_message("This feature can only be used in a server.", ephemeral=True)
        
        if not self.teams:
            return await inter.response.send_message("No teams added yet. Add teams first!", ephemeral=True)
        
        await inter.response.defer()
        
        channels = [
            discord.SelectOption(label=f"#{channel.name}", value=str(channel.id))
            for channel in inter.guild.text_channels
            if channel.permissions_for(inter.guild.me).send_messages
        ][:25]
        
        if not channels:
            return await self.ctx.error("No channels available to send to.")
        
        v = WolfView(self.ctx, timeout=60)
        v.add_item(ChannelSelector(channels))
        msg = await inter.followup.send("Select a channel to send the points table:", view=v, ephemeral=True)
        v.message = msg
        await v.wait()
        
        if not v.custom_id:
            return
        
        channel_id = int(v.custom_id[0])
        channel = inter.guild.get_channel(channel_id)
        
        if not channel or not isinstance(channel, discord.TextChannel):
            return await self.ctx.error("Channel not found or is not a text channel.")
        
        if not channel.permissions_for(inter.guild.me).send_messages:
            return await self.ctx.error(f"I don't have permission to send messages in {channel.mention}.")
        
        embed = discord.Embed(color=self.bot.color, title=self.header or "Tournament Points Table")
        embed.description = "**Rank | Team Name          | PP  | Kills | SD  | Total**\n```\n"
        
        for idx, team in enumerate(self.teams, 1):
            sd_indicator = "💎" if team.super_duper > 0 else "-"
            embed.description += (
                f"{idx:02}.   {team.name.ljust(20)} {str(team.placepts).ljust(4)} {str(team.kills).ljust(6)}"
                f"{sd_indicator.ljust(4)} {str(team.totalpts)}\n"
            )
        
        embed.description += "```"
        
        if self.footer:
            embed.set_footer(text=self.footer)
        
        if self.teams and any(t.logo for t in self.teams):
            first_team_with_logo = next((t for t in self.teams if t.logo), None)
            if first_team_with_logo:
                embed.set_thumbnail(url=first_team_with_logo.logo)
        
        await channel.send(embed=embed)
        await self.ctx.success(f"Points table sent to {channel.mention}!")

    @discord.ui.button(label="Create Image", style=discord.ButtonStyle.success)
    async def create_image(self, inter: discord.Interaction, btn: discord.Button):
        if not self.teams:
            return await inter.response.send_message("No teams added yet. Add teams first!", ephemeral=True)
        
        await inter.response.defer()
        
        v = WolfView(self.ctx, timeout=60)
        v.add_item(TableTypeSelector())
        msg = await inter.followup.send("Select table type:", view=v, ephemeral=True)
        v.message = msg
        await v.wait()
        
        if not v.custom_id:
            return
        
        table_type = v.custom_id[0]
        
        if table_type == "scrims":
            header = "Scrims Point Table"
        else:
            header = "Tournament Point Table"
        
        try:
            from ...helpers.image import create_points_table_image
            
            file = await create_points_table_image(
                teams=self.teams,
                header=self.header or header,
                footer=self.footer
            )
            
            await inter.followup.send(file=file, ephemeral=True)
        except Exception as e:
            await inter.followup.send(f"Error generating image: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Send Image", style=discord.ButtonStyle.success, row=1)
    async def send_image(self, inter: discord.Interaction, btn: discord.Button):
        if not inter.guild:
            return await inter.response.send_message("This feature can only be used in a server.", ephemeral=True)
        
        if not self.teams:
            return await inter.response.send_message("No teams added yet. Add teams first!", ephemeral=True)
        
        await inter.response.defer()
        
        v = WolfView(self.ctx, timeout=60)
        v.add_item(TableTypeSelector())
        msg = await inter.followup.send("Select table type:", view=v, ephemeral=True)
        v.message = msg
        await v.wait()
        
        if not v.custom_id:
            return
        
        table_type = v.custom_id[0]
        
        if table_type == "scrims":
            header = "Scrims Point Table"
        else:
            header = "Tournament Point Table"
        
        try:
            from ...helpers.image import create_points_table_image
            
            file = await create_points_table_image(
                teams=self.teams,
                header=self.header or header,
                footer=self.footer
            )
        except Exception as e:
            return await inter.followup.send(f"Error generating image: {str(e)}", ephemeral=True)
        
        channels = [
            discord.SelectOption(label=f"#{channel.name}", value=str(channel.id))
            for channel in inter.guild.text_channels
            if channel.permissions_for(inter.guild.me).send_messages
        ][:25]
        
        if not channels:
            return await self.ctx.error("No channels available to send to.")
        
        v2 = WolfView(self.ctx, timeout=60)
        v2.add_item(ChannelSelector(channels))
        msg2 = await inter.followup.send("Select a channel to send the image:", view=v2, ephemeral=True)
        v2.message = msg2
        await v2.wait()
        
        if not v2.custom_id:
            return
        
        channel_id = int(v2.custom_id[0])
        channel = inter.guild.get_channel(channel_id)
        
        if not channel or not isinstance(channel, discord.TextChannel):
            return await self.ctx.error("Channel not found or is not a text channel.")
        
        if not channel.permissions_for(inter.guild.me).send_messages:
            return await self.ctx.error(f"I don't have permission to send messages in {channel.mention}.")
        
        try:
            from ...helpers.image import create_points_table_image
            
            file = await create_points_table_image(
                teams=self.teams,
                header=self.header or header,
                footer=self.footer
            )
            
            await channel.send(file=file)
            await self.ctx.success(f"Points table image sent to {channel.mention}!")
        except Exception as e:
            await self.ctx.error(f"Error sending image: {str(e)}")


class HeaderInput(discord.ui.Modal, title="Set Title & Footer"):
    header = discord.ui.TextInput(
        label="Header (optional)",
        max_length=100,
        placeholder="Enter a title for the table",
    )
    footer = discord.ui.TextInput(
        label="Footer (optional)",
        max_length=100,
        placeholder="Enter a footer for the table",
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()


class TeamInput(discord.ui.Modal, title="Add New Team"):
    team_name = discord.ui.TextInput(
        label="Team Name",
        placeholder="Enter team name",
        max_length=20,
        min_length=4,
        required=True,
        style=discord.TextStyle.short,
    )

    kills = discord.ui.TextInput(
        label="No. of Kills",
        placeholder="Enter no. of kills",
        max_length=2,
        min_length=1,
        required=True,
    )

    placepts = discord.ui.TextInput(
        label="Place Points",
        placeholder="Enter placement points",
        max_length=2,
        min_length=1,
        required=True,
    )

    super_duper = discord.ui.TextInput(
        label="Super Duper (SD)",
        placeholder="Enter 1 for SD, 0 for none",
        max_length=1,
        min_length=1,
        required=False,
        default="0",
    )

    logo_url = discord.ui.TextInput(
        label="Logo URL (optional)",
        placeholder="Enter team logo URL",
        required=False,
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()


class TeamSelector(discord.ui.Select):
    view: WolfView

    def __init__(self, teams: T.List[Team]):
        _options = []
        for _ in teams:
            _options.append(discord.SelectOption(label=_.name, value=str(_.id), emoji=emote.TextChannel))

        super().__init__(placeholder="Select the teams you want to remove...", max_values=len(teams), options=_options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.custom_id = self.values
        self.view.stop()


class ChannelSelector(discord.ui.Select):
    view: WolfView

    def __init__(self, channels: T.List[discord.SelectOption]):
        super().__init__(placeholder="Select a channel to send the points table...", max_values=1, options=channels)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.custom_id = self.values
        self.view.stop()


class TableTypeSelector(discord.ui.Select):
    view: WolfView

    def __init__(self):
        options = [
            discord.SelectOption(label="Tournament", value="tournament", emoji="🏆"),
            discord.SelectOption(label="Scrims", value="scrims", emoji="⚔️")
        ]
        super().__init__(placeholder="Select table type...", max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.custom_id = self.values
        self.view.stop()
