import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from commands.chart import generate_stock_chart
from commands.formatting import format_error, format_response
from commands.health import get_server_status
from commands.help_data import (
    build_command_help_lines,
    build_help_overview_lines,
    normalize_help_command_name,
)
from commands.post import (
    SUPPORTED_DATE_FORMATS,
    build_post_channel_name,
    build_reverse_split_announcement,
    has_post_permission,
    parse_last_day_to_buy,
)
from commands.price import get_stock_price
from commands.rsa import calculate_reverse_split_arbitrage
from commands.test import test_all

# Load environment variables from .env file
load_dotenv()

# Retrieve sensitive information from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
POST_CATEGORY_ID_RAW = os.getenv("POST_CATEGORY_ID")
POST_MODERATOR_ROLE_ID_RAW = os.getenv("POST_MODERATOR_ROLE_ID")


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


POST_CATEGORY_ID = _parse_int(POST_CATEGORY_ID_RAW)
POST_MODERATOR_ROLE_ID = _parse_int(POST_MODERATOR_ROLE_ID_RAW)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Create the bot object with a command prefix (e.g., '!')
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


async def _send_command_error(ctx, action):
    logger.exception("%s command failed", action)
    await ctx.send(format_error(action, "Unexpected error. Check bot logs."))


@bot.event
async def on_ready():
    logger.info("Logged in as %s", bot.user.name)


@bot.command(name="help", help="Shows command usage and examples. Usage: !help [command].")
async def help_command(ctx, *, command_name: str = ""):
    normalized_name = normalize_help_command_name(command_name)
    no_mentions = discord.AllowedMentions.none()

    if not normalized_name:
        await ctx.send(
            format_response("Help", build_help_overview_lines()),
            allowed_mentions=no_mentions,
        )
        return

    resolved_name, lines = build_command_help_lines(normalized_name)
    if lines is None:
        await ctx.send(
            format_error("Help", f"Unknown command '{command_name}'. Use `!help` to list commands."),
            allowed_mentions=no_mentions,
        )
        return

    await ctx.send(
        format_response(f"Help: !{resolved_name}", lines),
        allowed_mentions=no_mentions,
    )


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


@bot.command(
    name="chart",
    help="Sends a dark mode stock chart. Usage: !chart [ticker] [period]. Default period is 1d. Periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max.",
)
async def chart(ctx, ticker: str, period: str = "1d"):
    chart_stream = None
    try:
        chart_stream, filename, caption, error_message = await asyncio.to_thread(
            generate_stock_chart,
            ticker,
            period,
        )
        if error_message:
            await ctx.send(error_message)
            return

        await ctx.send(content=caption, file=discord.File(fp=chart_stream, filename=filename))
    except Exception:
        await _send_command_error(ctx, "Chart")
    finally:
        if chart_stream is not None:
            chart_stream.close()


@bot.command(
    name="post",
    help="Creates a reverse split channel and announcement. Usage: !post [ticker] [split_ratio] [last_day_to_buy] [source_link].",
)
async def post(ctx, ticker: str, split_ratio: str, last_day_to_buy: str, source_link: str):
    if ctx.guild is None:
        await ctx.send(format_error("Post", "This command can only run in a server."))
        return

    if POST_MODERATOR_ROLE_ID is None:
        await ctx.send(format_error("Post", "POST_MODERATOR_ROLE_ID is not configured in .env"))
        return

    if not has_post_permission(ctx.author, POST_MODERATOR_ROLE_ID):
        await ctx.send(format_error("Post", f"Only users with role ID {POST_MODERATOR_ROLE_ID} can use this command."))
        return

    if not source_link.startswith(("http://", "https://")):
        await ctx.send(format_error("Post", "Source link must start with http:// or https://"))
        return

    if POST_CATEGORY_ID is None:
        await ctx.send(format_error("Post", "POST_CATEGORY_ID is not configured in .env"))
        return

    buy_date = parse_last_day_to_buy(last_day_to_buy)
    if buy_date is None:
        supported_formats = ", ".join(SUPPORTED_DATE_FORMATS)
        await ctx.send(
            format_error(
                "Post",
                f"Invalid last_day_to_buy date. Supported formats: {supported_formats}",
            )
        )
        return

    category = ctx.guild.get_channel(POST_CATEGORY_ID)
    if category is None:
        try:
            category = await ctx.guild.fetch_channel(POST_CATEGORY_ID)
        except discord.DiscordException:
            category = None

    if not isinstance(category, discord.CategoryChannel):
        await ctx.send(
            format_error(
                "Post",
                "Configured POST_CATEGORY_ID is missing or is not a category in this server.",
            )
        )
        return

    channel_name = build_post_channel_name(ticker, buy_date)
    if not channel_name:
        await ctx.send(format_error("Post", "Invalid ticker for channel name."))
        return

    reason = f"Reverse split post created by {ctx.author} for {ticker.upper()}"
    try:
        new_channel = await category.create_text_channel(channel_name, reason=reason)
        existing_text_channels = [channel for channel in category.text_channels if channel.id != new_channel.id]
        if existing_text_channels:
            top_text_channel = existing_text_channels[0]
            await new_channel.move(
                after=top_text_channel,
                category=category,
                reason="Place reverse split post second from top",
            )
    except discord.DiscordException:
        await ctx.send(format_error("Post", "Could not create the new channel in the target category."))
        return

    announcement = build_reverse_split_announcement(ticker, split_ratio, buy_date, source_link)
    try:
        await new_channel.send(
            announcement,
            allowed_mentions=discord.AllowedMentions(everyone=True),
        )
    except discord.DiscordException:
        await ctx.send(
            format_error(
                "Post",
                f"Created channel {new_channel.mention}, but failed to post announcement.",
            )
        )
        return

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
