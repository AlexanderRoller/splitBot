import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from commands.formatting import format_error, format_response
from commands.health import get_server_status
from commands.price import get_stock_price
from commands.rsa import calculate_reverse_split_arbitrage
from commands.test import test_all

# Load environment variables from .env file
load_dotenv()

# Retrieve sensitive information from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Create the bot object with a command prefix (e.g., '!')
bot = commands.Bot(command_prefix="!", intents=intents)


async def _send_command_error(ctx, action):
    logger.exception("%s command failed", action)
    await ctx.send(format_error(action, "Unexpected error. Check bot logs."))


@bot.event
async def on_ready():
    logger.info("Logged in as %s", bot.user.name)


@bot.command(name="price", help="Gets the current or most recent price of a specified stock ticker.")
async def fetch_stock_price(ctx, ticker: str):
    try:
        response = await asyncio.to_thread(get_stock_price, ticker)
        await ctx.send(response)
    except Exception:
        await _send_command_error(ctx, "Price Lookup")


@bot.command(name="health", help="Displays health information of the server and bot.")
async def health(ctx):
    try:
        response = await asyncio.to_thread(get_server_status)
        await ctx.send(response)
    except Exception:
        await _send_command_error(ctx, "Health Check")


@bot.command(name="rsa", help="Calculates the profitability of reverse split arbitrage.")
async def rsa(ctx, ticker: str, split_ratio: str):
    try:
        response = await asyncio.to_thread(calculate_reverse_split_arbitrage, ticker, split_ratio)
        await ctx.send(response)
    except Exception:
        await _send_command_error(ctx, "Reverse Split Arbitrage")


@bot.command(name="test_all", help="Tests all bot commands with sample inputs.")
async def run_all_tests(ctx):
    await test_all(ctx)


@bot.command(name="usercount", help="Returns the total number of users in the server.")
async def usercount(ctx):
    guild = ctx.guild

    response = format_error("User Count", "This command can only run in a server.")
    if guild:
        member_count = guild.member_count
        response = format_response("Server Members", [f"Members: {member_count}"])
    await ctx.send(response)


def main():
    token = (BOT_TOKEN or "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Configure BOT_TOKEN in your .env file.")
    bot.run(token)


if __name__ == "__main__":
    main()
