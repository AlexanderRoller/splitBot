import asyncio
import logging
import os
import time

import discord
from discord.ext import commands, tasks
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
COMMAND_TIMEOUT_SECONDS_RAW = os.getenv("COMMAND_TIMEOUT_SECONDS")
CHART_TIMEOUT_SECONDS_RAW = os.getenv("CHART_TIMEOUT_SECONDS")
TEST_ALL_TIMEOUT_SECONDS_RAW = os.getenv("TEST_ALL_TIMEOUT_SECONDS")


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


POST_CATEGORY_ID = _parse_int(POST_CATEGORY_ID_RAW)
POST_MODERATOR_ROLE_ID = _parse_int(POST_MODERATOR_ROLE_ID_RAW)
COMMAND_TIMEOUT_SECONDS = _parse_float(COMMAND_TIMEOUT_SECONDS_RAW) or 20.0
CHART_TIMEOUT_SECONDS = _parse_float(CHART_TIMEOUT_SECONDS_RAW) or 25.0
TEST_ALL_TIMEOUT_SECONDS = _parse_float(TEST_ALL_TIMEOUT_SECONDS_RAW) or 120.0
EVENT_LOOP_MONITOR_INTERVAL_SECONDS = 10.0
EVENT_LOOP_LAG_WARNING_SECONDS = 5.0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Create the bot object with a command prefix (e.g., '!')
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
_last_loop_tick = time.monotonic()


async def _send_command_error(ctx, action):
    logger.exception("%s command failed", action)
    await ctx.send(format_error(action, "Unexpected error. Check bot logs."))


@bot.event
async def on_ready():
    logger.info("Logged in as %s", bot.user.name)
    if not monitor_event_loop_lag.is_running():
        monitor_event_loop_lag.start()


@tasks.loop(seconds=EVENT_LOOP_MONITOR_INTERVAL_SECONDS)
async def monitor_event_loop_lag():
    global _last_loop_tick

    now = time.monotonic()
    lag_seconds = now - _last_loop_tick - EVENT_LOOP_MONITOR_INTERVAL_SECONDS
    _last_loop_tick = now
    if lag_seconds > EVENT_LOOP_LAG_WARNING_SECONDS:
        logger.warning(
            "Event loop lag detected: %.1fs (threshold %.1fs).",
            lag_seconds,
            EVENT_LOOP_LAG_WARNING_SECONDS,
        )


@monitor_event_loop_lag.before_loop
async def before_event_loop_monitor():
    await bot.wait_until_ready()


@bot.event
async def on_disconnect():
    logger.warning("Disconnected from Discord gateway.")


@bot.event
async def on_resumed():
    logger.info("Discord gateway session resumed.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingRequiredArgument):
        usage = None
        if ctx.command is not None:
            signature = (ctx.command.signature or "").strip()
            usage = f"!{ctx.command.qualified_name}".strip()
            if signature:
                usage = f"{usage} {signature}"

        detail = f"Missing required argument: `{error.param.name}`."
        if usage:
            detail = f"{detail} Usage: `{usage}`"
        await ctx.send(format_error("Command", detail))
        return

    if isinstance(error, commands.BadArgument):
        await ctx.send(format_error("Command", f"Invalid argument. {error}"))
        return

    if isinstance(error, commands.CommandInvokeError):
        logger.exception("Command invocation failed.", exc_info=error.original)
        return

    logger.exception("Unhandled command error.")
    await ctx.send(format_error("Command", "Unexpected command error. Check bot logs."))


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
        async with ctx.typing():
            response = await asyncio.wait_for(
                asyncio.to_thread(get_stock_price, ticker),
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
        await ctx.send(response)
    except asyncio.TimeoutError:
        await ctx.send(
            format_error(
                "Price Lookup",
                f"Timed out after {int(COMMAND_TIMEOUT_SECONDS)} seconds. Try again.",
            )
        )
    except Exception:
        await _send_command_error(ctx, "Price Lookup")


@bot.command(name="health", help="Displays health information of the server and bot.")
async def health(ctx):
    try:
        async with ctx.typing():
            response = await asyncio.wait_for(
                asyncio.to_thread(get_server_status),
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
        await ctx.send(response)
    except asyncio.TimeoutError:
        await ctx.send(
            format_error(
                "Health Check",
                f"Timed out after {int(COMMAND_TIMEOUT_SECONDS)} seconds. Try again.",
            )
        )
    except Exception:
        await _send_command_error(ctx, "Health Check")


@bot.command(name="rsa", help="Calculates reverse split arbitrage profitability. Ratio format: small:big (example: 1:10).")
async def rsa(ctx, ticker: str, split_ratio: str):
    try:
        async with ctx.typing():
            response = await asyncio.wait_for(
                asyncio.to_thread(calculate_reverse_split_arbitrage, ticker, split_ratio),
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
        await ctx.send(response)
    except asyncio.TimeoutError:
        await ctx.send(
            format_error(
                "Reverse Split Arbitrage",
                f"Timed out after {int(COMMAND_TIMEOUT_SECONDS)} seconds. Try again.",
            )
        )
    except Exception:
        await _send_command_error(ctx, "Reverse Split Arbitrage")


@bot.command(
    name="chart",
    help="Sends a dark mode stock chart. Usage: !chart [ticker] [period]. Default period is 1d. Periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max.",
)
async def chart(ctx, ticker: str, period: str = "1d"):
    chart_stream = None
    try:
        async with ctx.typing():
            chart_stream, filename, caption, error_message = await asyncio.wait_for(
                asyncio.to_thread(
                    generate_stock_chart,
                    ticker,
                    period,
                ),
                timeout=CHART_TIMEOUT_SECONDS,
            )
        if error_message:
            await ctx.send(error_message)
            return

        await ctx.send(content=caption, file=discord.File(fp=chart_stream, filename=filename))
    except asyncio.TimeoutError:
        await ctx.send(
            format_error(
                "Chart",
                f"Timed out after {int(CHART_TIMEOUT_SECONDS)} seconds while generating chart data. Try again.",
            )
        )
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
    try:
        async with ctx.typing():
            await asyncio.wait_for(test_all(ctx), timeout=TEST_ALL_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        await ctx.send(
            format_error(
                "Test Run",
                f"Timed out after {int(TEST_ALL_TIMEOUT_SECONDS)} seconds.",
            )
        )
    except Exception:
        await _send_command_error(ctx, "Test Run")


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
