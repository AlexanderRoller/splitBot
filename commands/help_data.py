HELP_ORDER = [
    "help",
    "price",
    "chart",
    "post",
    "rsa",
    "health",
    "usercount",
    "test_all",
]

HELP_COMMANDS = {
    "help": {
        "usage": "!help [command]",
        "description": "Shows command usage and examples.",
        "examples": [
            "!help",
            "!help chart",
        ],
    },
    "price": {
        "usage": "!price <ticker>",
        "description": "Fetches the current or most recent stock price plus daily change.",
        "examples": [
            "!price AAPL",
            "!price NVDA",
        ],
    },
    "chart": {
        "usage": "!chart <ticker> [period]",
        "description": "Generates a dark mode stock chart image. Default period is 1d.",
        "details": [
            "Valid periods: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `max`.",
        ],
        "examples": [
            "!chart TSLA",
            "!chart AAPL 6mo",
        ],
    },
    "post": {
        "usage": "!post <ticker> <split_ratio> <last_day_to_buy> <source_link>",
        "description": "Creates a new reverse split channel in the configured category and posts an `@everyone` alert.",
        "details": [
            "Access: only users with the configured moderator role ID can run this command.",
            "Date formats: `YYYY-MM-DD`, `MM/DD/YYYY`, `Mon-DD-YYYY`, `Month DD, YYYY`, `MM/DD`, `Mon-DD`.",
            "Displayed date format: `Mon D` (example: `Feb 12`).",
            "Channel format: `\N{ALARM CLOCK}-ticker-mon-day` (example: `\N{ALARM CLOCK}-aapl-feb-12`).",
        ],
        "examples": [
            "!post AAPL 1:10 2026-02-20 https://example.com/source",
            "!post TSLA 1:5 Feb-20 https://example.com/source",
        ],
    },
    "rsa": {
        "usage": "!rsa <ticker> <split_ratio>",
        "description": "Estimates profitability of a reverse split arbitrage setup.",
        "details": [
            "Split ratio format must be small:big (example: `1:10`).",
        ],
        "examples": [
            "!rsa AAPL 1:10",
            "!rsa TSLA 1:5",
        ],
    },
    "health": {
        "usage": "!health",
        "description": "Shows server health details (CPU, memory, disk, temperature, uptime).",
        "examples": [
            "!health",
        ],
    },
    "usercount": {
        "usage": "!usercount",
        "description": "Returns the total number of members in the current server.",
        "examples": [
            "!usercount",
        ],
    },
    "test_all": {
        "usage": "!test_all",
        "description": "Runs a quick sample check for bot commands.",
        "examples": [
            "!test_all",
        ],
    },
}


def normalize_help_command_name(value):
    key = str(value or "").strip().lower()
    if key.startswith("!"):
        key = key[1:]
    return key


def build_instructions_message():
    return (
        "🚀 Welcome to the Burry Deez Bot! 🚀\n\n"
        "Stay on top of stocks with quick lookups, reverse split arbitrage estimates, chart snapshots, "
        "and moderator tools for split alerts.\n\n"
        "### 💼 **Commands:**\n\n"
        "1. **`!help [command]`**\n"
        "   - Shows usage and examples for all commands or a specific command.\n"
        "   - Example: `!help post`\n\n"
        "2. **`!price [ticker]`**\n"
        "   - Fetches the latest available stock price and daily change.\n"
        "   - Example: `!price AAPL`\n\n"
        "3. **`!chart [ticker] [period]`**\n"
        "   - Sends a dark mode stock chart image (default period: `1d`).\n"
        "   - Example: `!chart TSLA 6mo`\n\n"
        "4. **`!rsa [ticker] [split ratio]`**\n"
        "   - Estimates reverse split arbitrage profitability.\n"
        "   - Ratio format: small:big (example: `1:10`).\n"
        "   - Example: `!rsa AAPL 1:10`\n\n"
        "5. **`!post [ticker] [split ratio] [last day to buy] [source link]`**\n"
        "   - Creates a reverse split channel and posts an `@everyone` announcement.\n"
        "   - Restricted to users with the configured moderator role ID.\n"
        "   - Example: `!post AAPL 1:10 2026-02-20 https://example.com/source`\n\n"
        "6. **`!health`**\n"
        "   - Shows server health (CPU, memory, disk, uptime, temp if available).\n"
        "   - Example: `!health`\n\n"
        "7. **`!usercount`**\n"
        "   - Shows the total number of members in the server.\n"
        "   - Example: `!usercount`\n\n"
        "8. **`!test_all`**\n"
        "   - Runs sample checks for key bot commands.\n"
        "   - Example: `!test_all`\n\n"
        "---\n\n"
        "### 🔔 **Automatic Posts:**\n\n"
        "- No scheduled automatic posts are enabled.\n"
        "- Use `!post` to create reverse split announcement channels on demand.\n\n"
        "**Burry Deez Bot is open-source!**\n"
        "Check out the repository and contribute here:\n"
        "**[Burry Deez GitHub](https://github.com/AlexanderRoller/BurryDeez)**"
    )


def build_command_help_lines(command_name):
    key = normalize_help_command_name(command_name)
    command_help = HELP_COMMANDS.get(key)
    if command_help is None:
        return None, None

    lines = [
        f"Usage: `{command_help['usage']}`",
        f"Description: {command_help['description']}",
    ]

    for detail in command_help.get("details", []):
        lines.append(detail)

    lines.append("Examples:")
    for example in command_help["examples"]:
        lines.append(f"`{example}`")

    return key, lines
