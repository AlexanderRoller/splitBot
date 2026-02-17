# splitBot

A Discord bot for quick stock utilities, chart snapshots, reverse split workflows, and basic server diagnostics.

> This project was previously named **BurryDeez**. The GitHub repo has been renamed to **splitBot**.

## Features

- `!price` — live/recent stock price + daily change
- `!chart` — dark mode chart image for a ticker
- `!rsa` — reverse split arbitrage estimate
- `!post` — moderator-only reverse split channel creation + announcement
- `!health` — server health summary
- `!usercount` — total member count
- `!help` — instruction message + command-specific help

## Requirements

- **Python 3.11+** (Python **3.12 recommended**)
- A Discord bot token from the Discord Developer Portal
- Network access from the host running the bot

Python dependencies are listed in `requirements.txt`.

## Quick start (macOS / Linux)

1) Clone the repo

```bash
git clone https://github.com/AlexanderRoller/splitBot.git
cd splitBot
```

2) Create a virtual environment + install deps

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3) Create a `.env`

```dotenv
# required
BOT_TOKEN=your_discord_bot_token

# required for !post
POST_CATEGORY_ID=123456789012345678
POST_MODERATOR_ROLE_ID=123456789012345678

# optional timeouts (seconds)
COMMAND_TIMEOUT_SECONDS=20
CHART_TIMEOUT_SECONDS=25
TEST_ALL_TIMEOUT_SECONDS=120
```

4) Run

```bash
python main.py
```

## Quick start (Windows PowerShell)

```powershell
git clone https://github.com/AlexanderRoller/splitBot.git
cd splitBot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## Discord bot setup notes

In the Discord Developer Portal:

- Enable **Message Content Intent** (this bot uses `!commands`, so it needs message content).
- Invite the bot to your server with permissions to:
  - Read messages / read message history
  - Send messages
  - Attach files (for `!chart` images)
  - Manage channels (only if you will use `!post`)

## Running as a service (recommended)

If you want splitBot to restart automatically after reboots/crashes, run it under a process supervisor.

### macOS (launchd)

This repo includes a LaunchAgent plist and start script:

- `deploy/macos/com.lex.splitbot.plist`
- `scripts/start_splitbot.sh`

See: `deploy/macos/README.md`

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | Yes | Discord bot token. |
| `POST_CATEGORY_ID` | Yes for `!post` | Category where `!post` creates channels. |
| `POST_MODERATOR_ROLE_ID` | Yes for `!post` | Only users with this role ID can run `!post`. |
| `COMMAND_TIMEOUT_SECONDS` | No | Timeout for blocking data commands like `!price`, `!health`, `!rsa`. Default: `20`. |
| `CHART_TIMEOUT_SECONDS` | No | Timeout for chart generation in `!chart`. Default: `25`. |
| `TEST_ALL_TIMEOUT_SECONDS` | No | Timeout for `!test_all`. Default: `120`. |

## Command reference

| Command | Description | Example |
|---|---|---|
| `!help [command]` | Shows the full bot instructions or details for one command. | `!help post` |
| `!price [ticker]` | Fetches latest available stock price and daily change. | `!price AAPL` |
| `!chart [ticker] [period]` | Sends a dark mode chart image (default period `1d`). Valid periods: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `max`. | `!chart TSLA 6mo` |
| `!rsa [ticker] [split_ratio]` | Estimates reverse split arbitrage profitability. Ratio must be `small:big` (example: `1:10`). | `!rsa AAPL 1:10` |
| `!post [ticker] [split_ratio] [last_day_to_buy] [source_link]` | Creates a reverse split channel and posts an `@everyone` announcement. Restricted by role ID. | `!post AAPL 1:10 2026-02-20 https://example.com/source` |
| `!health` | Shows CPU, memory, disk, uptime, and temperature (if available). | `!health` |
| `!usercount` | Shows total server members. | `!usercount` |
| `!test_all` | Runs sample checks for key commands. | `!test_all` |

## `!post` behavior

- Access control: role ID only (`POST_MODERATOR_ROLE_ID`)
- Channel naming: `⏰-ticker-mon-day` (example: `⏰-aapl-feb-12`)
- Date input accepted:
  - `YYYY-MM-DD`
  - `MM/DD/YYYY`
  - `Mon-DD-YYYY`
  - `Month DD, YYYY`
  - `MM/DD`
  - `Mon-DD`
- Displayed date in announcement: `Mon D` (example: `Feb 12`)
- New channel placement: second from top in the target category

## Testing

```bash
python -m unittest discover -q
```

## Troubleshooting

- If you see missing permission errors for `!post`, ensure the bot role has **Manage Channels** and the configured `POST_CATEGORY_ID` exists.
- If `!chart` fails on a headless server, ensure matplotlib can render (some environments may require additional system fonts).
- For always-on usage, prefer a wired connection and a host that does not sleep.

## License

See `LICENSE`.
