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


def build_help_overview_lines():
    lines = ["Use `!help <command>` for full usage and examples."]
    for command_name in HELP_ORDER:
        command_help = HELP_COMMANDS[command_name]
        lines.append(f"`{command_help['usage']}` - {command_help['description']}")
        lines.append(f"Example: `{command_help['examples'][0]}`")
    return lines


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
