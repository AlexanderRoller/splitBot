import discord
import os
from discord.ext import tasks, commands
from dotenv import load_dotenv
import schwabdev
import json

# load custom commands
from commands.price import get_stock_price
from commands.health import get_server_status
from commands.options_arb import calculate_options_arbitrage
from commands.value import calculate_intrinsic_value
from commands.spread import get_option_prices
from commands.rsa import calculate_reverse_split_arbitrage
from commands.occ import send_occ_alerts
from commands.sec import send_sec_alerts
from commands.test import test_all

# Load environment variables from .env file
load_dotenv()

# Retrieve sensitive information from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
OCC_RSS_URL = os.getenv('RSS_URL')
SEC_RSS_URL = os.getenv('SEC_RSS_URL')

#connect to schwab api
load_dotenv()
client = schwabdev.Client(os.getenv('app_key'), os.getenv('app_secret'), os.getenv('callback_url'))

# Define the intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Create the bot object with a command prefix (e.g., '!')
bot = commands.Bot(command_prefix='!', intents=intents)

# A set to keep track of already seen entries to avoid duplicate notifications
seen_entries = set()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_feed.start()  # Start the feed checking loop

@bot.command(name='price', help='Gets the current or most recent price of a specified stock ticker.')
async def fetch_stock_price(ctx, ticker: str):
    try:
        response = get_stock_price(ticker, client)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Error fetching stock price: {str(e)}")

@bot.command(name='health', help='Displays health information of the server and bot.')
async def health(ctx):
    try:
        response = get_server_status()
        # Adding the Terminator-themed quip
        response += "\n🦾 *I'll be back... if the CPU doesn't melt first!*"
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Error fetching health status: {str(e)}")

@bot.command(name='arb', help='Calculates arbitrage opportunity of non-standard options.')
async def calculate_arb(ctx, ticker: str, strike_price: float, split_ratio: str = None):
    try:
        response = calculate_options_arbitrage(ticker, strike_price, split_ratio)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Error calculating arbitrage: {str(e)}")

@bot.command(name='value', help='Calculates the intrinsic value of an options contract.')
async def value(ctx, option_type: str, ticker: str, strike_price: float):
    try:
        response = calculate_intrinsic_value(option_type, ticker, strike_price)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Error calculating intrinsic value: {str(e)}")


@bot.command(name='spread', help='Calculates the ask, bid, and mark prices of an options contract.')
async def spread(ctx, ticker: str, strike_price: float, expiration_date: str, option_type: str):
    try:
        response = get_option_prices(ticker, expiration_date, strike_price, option_type)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Error fetching options spread: {str(e)}")

@bot.command(name='rsa', help='Calculates the profitability of reverse split arbitrage.')
async def rsa(ctx, ticker: str, split_ratio: str):
    try:
        response = calculate_reverse_split_arbitrage(ticker, split_ratio, client)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Error calculating reverse split arbitrage: {str(e)}")

@bot.command(name="test_all", help="Tests all bot commands with sample inputs.")
async def run_all_tests(ctx):
    await test_all(ctx, bot, OCC_RSS_URL, SEC_RSS_URL, seen_entries)

@bot.command(name='usercount', help='Returns the total number of users in the server.')
async def usercount(ctx):
    # Get the total number of members in the server (guild)
    guild = ctx.guild
    member_count = guild.member_count
    
    # Send a message with the member count
    response = f"👥 **This server has {member_count} members!**"
    await ctx.send(response)

@tasks.loop(minutes=1)
async def check_feed():
    print("Checking feed for updates...")
    channel = bot.get_channel(CHANNEL_ID)
    
    if not channel:
        print(f"Failed to get channel with ID {CHANNEL_ID}")
        return

    try:
        # Check OCC feed and send alerts
        await send_occ_alerts(channel, OCC_RSS_URL, seen_entries)
    except Exception as e:
        print(f"Error checking OCC feed: {str(e)}")
    
    try:
        # Check SEC feed and send alerts
        await send_sec_alerts(channel, SEC_RSS_URL, seen_entries)
    except Exception as e:
        print(f"Error checking SEC feed: {str(e)}")

@check_feed.before_loop
async def before_check_feed():
    await bot.wait_until_ready()

bot.run(BOT_TOKEN)
