"""
Leveling Cog for Discord Bot

This file provides a Discord bot cog for implementing a leveling system. Users earn XP and can check their level, view the leaderboard, and more.

Author: Mindset
GitHub: https://github.com/mindsetpro
Discord: https://discord.gg/t9Vhe8mT3P

Requirements:
- disnake: https://github.com/EQUENOS/disnake

Usage:
1. Add the LevelCog to your Discord bot using the setup function.
2. Users earn XP as they interact with the server.
3. Commands:
   - !lvl: Check your current level and rank.
   - !lb or !leaderboard: View the server leaderboard.
   - !xp: Check your current XP.

Note: Ensure you have the required assets (images, fonts) in the specified paths.

"""

import disnake
from disnake.ext import commands
import os
import aiohttp
import random
from typing import Optional
from disnake.ui import Button, View
import math
from math import floor

ASSETS_PATH = "assets"
FONTS_PATH = "fonts"
TMP_PATH = "tmp"
XP_PER_LVL = 100

class LevelCog(commands.Cog, name="Leveling"):
    def __init__(self, bot):
        self.bot = bot
        self.ASSETS_PATH = "./assets"
        self.FONTS_PATH = "./fonts"
        self.TMP_PATH = "./tmp"
        self.XP_PER_LVL = 100

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")

    # ... (other event listeners)

    @commands.command(name='lvl')
    async def level_command(self, ctx):
        user = ctx.author
        guild_id = ctx.guild.id
        username = user.display_name
        rank = self.get_rank(user.id, guild_id)
        xp = xp_data[guild_id].get(user.id, 0)
        image_path = await self.render_lvl_image(user, username, xp, rank)

        if image_path:
            await ctx.send(f"Hello, {user.mention}! Here's your rank!", file=disnake.File(image_path))
            os.remove(image_path)

    @commands.command(name='lb', aliases=['leaderboard'])
    async def leaderboard_command(self, ctx):
        guild_id = ctx.guild.id
        sorted_users = sorted(xp_data.get(guild_id, {}).items(), key=lambda x: x[1], reverse=True)
        top_ten = sorted_users[:10]

        leaderboard_text = "**Leaderboard**:\n"
        for i, (user_id, xp) in enumerate(top_ten):
            user = ctx.guild.get_member(user_id)
            if user:
                leaderboard_text += f"**__{i + 1}__**: {user.display_name} - {xp} XP\n"

        await ctx.send(leaderboard_text)

    @commands.command(name='xp')
    async def xp_command(self, ctx):
        user = ctx.author
        guild_id = ctx.guild.id
        await ctx.send(f"{user.mention}, Your current XP: {self.get_xp(user.id, guild_id)}")

async def update_user_count(guild: discord.Guild):
    activity_mes = f"{guild.member_count} members!"
    activity_object = discord.Activity(name=activity_mes, type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity_object)

async def download_avatar(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                with open(filename, 'wb') as f:
                    f.write(data)
                return True
    return False

async def render_level_up_image(user: discord.Member, old_level: int, new_level: int) -> Optional[str]:
    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)

    out_filename = os.path.join(TMP_PATH, f"level_up_{user.id}_{user.guild.id}.png")

    bg = Image.open(IMG_BG2)
    frame = Image.open(IMG_FRAME2)

    bg.paste(frame, (14, 12), frame)

    draw = ImageDraw.Draw(bg)
    font_22 = ImageFont.load_default()

    # Add big text in the middle
    level_text = f"{old_level} -> {new_level}"
    level_width = font_22.getlength(level_text)
    draw.text((bg.width // 2 - level_width // 2, bg.height // 2 - 10), level_text, FONT_COLOR, font=font_22)

    bg.save(out_filename)
    bg.close()
    frame.close()

    return out_filename

async def render_lvl_image(user: discord.Member, username: str, xp: int, rank: int) -> Optional[str]:
    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)

    lvl = floor(xp / XP_PER_LVL)
    bar_num = math.ceil(10 * (xp - (lvl * XP_PER_LVL)) / XP_PER_LVL)

    out_filename = os.path.join(TMP_PATH, f"{user.id}_{user.guild.id}.png")
    avatar_filename = out_filename

    avatar_url = user.display_avatar.url

    success = await download_avatar(avatar_url, avatar_filename)
    if not success:
        return None

    bg = Image.open(IMG_BG)
    avatar = Image.open(avatar_filename).convert("RGBA")
    frame = Image.open(IMG_FRAME)
    small_bar = Image.open(IMG_SM_BAR)
    large_bar = Image.open(IMG_LG_BAR)

    avatar = avatar.resize((68, 68))
    bg.paste(avatar, (16, 14), avatar)
    bg.paste(frame, (14, 12), frame)

    for i in range(0, bar_num):
        if i % 5 == 4:
            bg.paste(large_bar, (BAR_X[i], BAR_Y), large_bar)
        else:
            bg.paste(small_bar, (BAR_X[i], BAR_Y), small_bar)

    draw = ImageDraw.Draw(bg)
    font_14 = ImageFont.load_default()
    font_22 = ImageFont.load_default()
    
    draw.text(USERNAME_POS.shadow_tuple(), username, BACK_COLOR, font=font_22)
    draw.text(USERNAME_POS.as_tuple(), username, FONT_COLOR, font=font_22)

    draw.text(LEVEL_POS.shadow_tuple(), f"Level {lvl}", BACK_COLOR, font=font_22)
    draw.text(LEVEL_POS.as_tuple(), f"Level {lvl}", FONT_COLOR, font=font_22)

    rank_text = f"Server Rank : {rank}"
    rank_width = font_14.getlength(rank_text)
    draw.text((RANK_POS.x - rank_width, RANK_POS.y), rank_text, BACK_COLOR, font=font_14)

    bg.save(out_filename)
    bg.close()
    avatar.close()
    frame.close()
    small_bar.close()
    large_bar.close()

    return out_filename

def get_xp(user_id, guild_id):
    return f"{xp_data.get(guild_id, {}).get(user_id, 0)} XP"

def get_rank(user_id, guild_id):
    sorted_users = sorted(xp_data.get(guild_id, {}).items(), key=lambda x: x[1], reverse=True)
    user_rank = next((i+1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id), None)
    return user_rank

def setup(bot):
    bot.add_cog(LevelCog(bot))
