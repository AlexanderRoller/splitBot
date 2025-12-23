import discord
import os
from datetime import time, timezone
from discord.ext import commands, tasks
from dotenv import load_dotenv

# load custom commands
from commands.formatting import format_error, format_response
from commands.economic_calendar import get_week_start, summarize_weekly_calendar
from commands.price import get_stock_price
from commands.health import get_server_status
from commands.rsa import calculate_reverse_split_arbitrage
from commands.test import test_all

# Load environment variables from .env file
load_dotenv()

# Retrieve sensitive information from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEEKLY_SUMMARY_CHANNEL_ID = os.getenv('WEEKLY_SUMMARY_CHANNEL_ID')
WEEKLY_SUMMARY_DAY = os.getenv('WEEKLY_SUMMARY_DAY')
WEEKLY_SUMMARY_TIME_UTC = os.getenv('WEEKLY_SUMMARY_TIME_UTC', '23:00')

def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def _parse_time(value):
    if not value:
        return None
    parts = value.split(':')
    if len(parts) != 2:
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return None
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None
    return time(hour=hour, minute=minute, tzinfo=timezone.utc)

WEEKLY_SUMMARY_CHANNEL_ID = _parse_int(WEEKLY_SUMMARY_CHANNEL_ID)
WEEKLY_SUMMARY_DAY = _parse_int(WEEKLY_SUMMARY_DAY)
if WEEKLY_SUMMARY_DAY is None or WEEKLY_SUMMARY_DAY < 0 or WEEKLY_SUMMARY_DAY > 6:
    WEEKLY_SUMMARY_DAY = 4

WEEKLY_SUMMARY_TIME = _parse_time(WEEKLY_SUMMARY_TIME_UTC)
if WEEKLY_SUMMARY_TIME is None:
    WEEKLY_SUMMARY_TIME = time(hour=23, minute=0, tzinfo=timezone.utc)

# Define the intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Create the bot object with a command prefix (e.g., '!')
bot = commands.Bot(command_prefix='!', intents=intents)
last_weekly_summary_start = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    if not weekly_calendar_summary.is_running():
        weekly_calendar_summary.start()

@bot.command(name='price', help='Gets the current or most recent price of a specified stock ticker.')
async def fetch_stock_price(ctx, ticker: str):
    try:
        response = get_stock_price(ticker)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(format_error("Price Lookup", str(e)))

@bot.command(name='health', help='Displays health information of the server and bot.')
async def health(ctx):
    try:
        response = get_server_status()
        await ctx.send(response)
    except Exception as e:
        await ctx.send(format_error("Health Check", str(e)))

@bot.command(name='rsa', help='Calculates the profitability of reverse split arbitrage.')
async def rsa(ctx, ticker: str, split_ratio: str):
    try:
        response = calculate_reverse_split_arbitrage(ticker, split_ratio)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(format_error("Reverse Split Arbitrage", str(e)))

@bot.command(name='calendar', help='Summarizes the current economic weekly calendar from MarketWatch.')
async def calendar(ctx):
    try:
        response = summarize_weekly_calendar(include_command=True)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(format_error("Economic Calendar", str(e)))

@bot.command(name="test_all", help="Tests all bot commands with sample inputs.")
async def run_all_tests(ctx):
    await test_all(ctx)

@bot.command(name='usercount', help='Returns the total number of users in the server.')
async def usercount(ctx):
    # Get the total number of members in the server (guild)
    guild = ctx.guild
    
    # Send a message with the member count
    response = format_error("User Count", "This command can only run in a server.")
    if guild:
        member_count = guild.member_count
        response = format_response("Server Members", [f"Members: {member_count}"])
    await ctx.send(response)

@tasks.loop(time=WEEKLY_SUMMARY_TIME)
async def weekly_calendar_summary():
    if WEEKLY_SUMMARY_CHANNEL_ID is None:
        return

    now = discord.utils.utcnow().date()
    if now.weekday() != WEEKLY_SUMMARY_DAY:
        return

    global last_weekly_summary_start
    week_start = get_week_start(now)
    if last_weekly_summary_start == week_start:
        return

    channel = bot.get_channel(WEEKLY_SUMMARY_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(WEEKLY_SUMMARY_CHANNEL_ID)
        except discord.DiscordException:
            return

    message = summarize_weekly_calendar(
        include_command=False,
        title_prefix="Weekly Economic Calendar Summary",
    )
    if message.startswith("**Economic Calendar Error**"):
        print(message)
        return
    await channel.send(message)
    last_weekly_summary_start = week_start

@weekly_calendar_summary.before_loop
async def before_weekly_calendar_summary():
    await bot.wait_until_ready()

bot.run(BOT_TOKEN)
