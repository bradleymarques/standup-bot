import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN: str = os.environ.get("DISCORD_BOT_TOKEN", "")
DISCORD_GUILD_ID: int = int(os.environ.get("DISCORD_GUILD_ID", "0"))

from discord import Intents, Interaction, Member

from standup_bot import StandupBot

intents: Intents = Intents.default()
intents.members = True

bot: StandupBot = StandupBot(guild_id=DISCORD_GUILD_ID, intents=intents)


@bot.tree.command()
async def start_standup(interaction: Interaction):
    """Start a standup in a voice channel"""
    await bot.start_standup(interaction)


@bot.tree.command()
async def end_standup(interaction: Interaction):
    """End standup"""
    await bot.end_standup(interaction)


@bot.tree.command()
async def been(interaction: Interaction, member: Member):
    """Mark that a member has been"""
    await bot.member_been(interaction, member)


bot.run(DISCORD_BOT_TOKEN)
