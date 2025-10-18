from pathlib import Path
from typing import List, Optional
import asyncio
import io
import random

import aiohttp
import discord
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def add_watermark(image, footer: str):
    """Add a watermark/footer text to the bottom right of the image."""
    if not footer:
        return
    
    width, height = image.size
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype(str(Path.cwd() / "src" / "data" / "font" / "Ubuntu-Regular.ttf"), 25)
    
    bbox = draw.textbbox((0, 0), footer, font=font)
    textwidth = bbox[2] - bbox[0]
    textheight = bbox[3] - bbox[1]
    
    margin = 20
    x = width - textwidth - margin
    y = height - textheight - margin
    
    draw.text((x, y), footer, font=font, fill=(255, 255, 255))


def add_title(image, title: str):
    """Add a title to the top of the image."""
    if not title:
        return
    
    font = ImageFont.truetype(str(Path.cwd() / "src" / "data" / "font" / "robo-bold.ttf"), 90)
    draw = ImageDraw.Draw(image)
    
    bbox = draw.textbbox((0, 0), title.upper(), font=font)
    w = bbox[2] - bbox[0]
    
    left = (image.width - w) / 2
    top = 50
    
    draw.text((left, top), title.upper(), font=font, fill=(255, 255, 255))


def create_header_rect():
    """Create the header rectangle with column titles."""
    rect = Image.open(str(Path.cwd() / "src" / "data" / "img" / "rect2.png"))
    rect = rect.convert("RGBA")
    rect = rect.resize((round(rect.size[0] / 1.5), round(rect.size[1] / 1.4)))
    
    draw = ImageDraw.Draw(rect)
    font = ImageFont.truetype(str(Path.cwd() / "src" / "data" / "font" / "robo-italic.ttf"), 16)
    
    top = 10
    fill = (0, 0, 0)
    
    draw.text((16, top), "RANK", fill, font=font)
    draw.text((220, top), "TEAM NAME", fill, font=font)
    draw.text((612, top), "PLACE PTS", fill, font=font)
    draw.text((744, top), "KILL PTS", fill, font=font)
    draw.text((870, top), "TOTAL PTS", fill, font=font)
    draw.text((1024, top), "CD", fill, font=font)
    
    return rect


async def download_logo(url: str) -> Optional[Image.Image]:
    """Download and resize a team logo from URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    logo = Image.open(io.BytesIO(data))
                    logo = logo.convert("RGBA")
                    logo.thumbnail((40, 40), Image.Resampling.LANCZOS)
                    return logo
    except Exception:
        pass
    return None


def create_team_rects(teams: List, logos: Optional[dict] = None) -> list:
    """Create individual rectangles for each team."""
    font = ImageFont.truetype(str(Path.cwd() / "src" / "data" / "font" / "robo-bold.ttf"), 24)
    top, left = 10, 16
    
    if logos is None:
        logos = {}
    
    _list = []
    for idx, team in enumerate(teams, start=1):
        image = Image.open(str(Path.cwd() / "src" / "data" / "img" / "rect2.png"))
        image = image.convert("RGBA")
        image = image.resize((round(image.size[0] / 1.5), round(image.size[1] / 1.4)))
        
        draw = ImageDraw.Draw(image)
        
        draw.rectangle(((0, 0), (image.width, image.height)), fill=(30, 144, 255, 255))
        
        team_name = team.name[:20]
        sd_text = "💎" if team.super_duper > 0 else "-"
        
        draw.text((left, top), f"#{idx:02}", (255, 255, 255), font=font)
        
        logo_offset = 0
        if team.logo and team.logo in logos:
            logo_img = logos[team.logo]
            if logo_img:
                image.paste(logo_img, (left + 80, top - 4), logo_img)
                logo_offset = 50
        
        draw.text((left + 204 + logo_offset, top), team_name, (255, 255, 255), font=font)
        draw.text((left + 596, top), f"{team.placepts:02}", (255, 255, 255), font=font)
        draw.text((left + 728, top), f"{team.kills:02}", (255, 255, 255), font=font)
        draw.text((left + 854, top), f"{team.totalpts:02}", (255, 255, 255), font=font)
        draw.text((left + 1008, top), sd_text, (255, 255, 255), font=font)
        
        _list.append(image)
    
    return _list


async def create_points_table_image(teams: List, header: Optional[str] = None, footer: Optional[str] = None) -> discord.File:
    """Create a points table image from teams data."""
    
    logos = {}
    for team in teams:
        if team.logo and team.logo not in logos:
            logo_img = await download_logo(team.logo)
            if logo_img:
                logos[team.logo] = logo_img
    
    def _wrapper():
        team_rects = create_team_rects(teams, logos)
        
        number = random.choice(range(1, 7))
        bg_path = Path.cwd() / "src" / "data" / "img" / f"ptable{number}.jpg"
        
        image = Image.open(str(bg_path))
        image = image.resize((1250, 938))
        image = image.filter(ImageFilter.GaussianBlur(1))
        
        header_rect = create_header_rect()
        image.paste(header_rect, (46, 240), header_rect)
        
        top = 310
        for rect in team_rects[:10]:
            image.paste(rect, (46, top), rect)
            top += 50
        
        if header:
            add_title(image, header)
        
        if footer:
            add_watermark(image, footer)
        
        img_bytes = io.BytesIO()
        image.save(img_bytes, "PNG")
        img_bytes.seek(0)
        
        return discord.File(img_bytes, "points_table.png")
    
    return await asyncio.get_event_loop().run_in_executor(None, _wrapper)
