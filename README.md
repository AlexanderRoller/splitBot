# splitBot (formerly BurryDeez)

splitBot is a Discord bot for quick stock utilities, chart snapshots, reverse split workflows, and basic server diagnostics.

## Features

- `!price`: live/recent stock price + daily change
- `!chart`: dark mode chart image for a ticker
- `!rsa`: reverse split arbitrage estimate
- `!post`: moderator-only reverse split channel creation + announcement
- `!health`: server health summary
- `!usercount`: total member count
- `!help`: instruction message + command-specific help

## Requirements

- Python 3.11 or 3.12 recommended for best runtime stability
- A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)
- Packages in `requirements.txt`:
  - `discord.py`
  - `yfinance`
  - `psutil`
  - `python-dotenv`
  - `matplotlib`

## Quick Start

1. Clone the repo:

   ```bash
   git clone https://github.com/AlexanderRoller/splitBot.git
   cd BurryDeez  # local folder name (optional: rename folder to splitBot)
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` in the project root:

   ```dotenv
   BOT_TOKEN=your_discord_bot_token
   POST_CATEGORY_ID=your_target_category_id
   POST_MODERATOR_ROLE_ID=123456789012345678
   # Optional reliability timeouts (seconds)
   COMMAND_TIMEOUT_SECONDS=20
   CHART_TIMEOUT_SECONDS=25
   TEST_ALL_TIMEOUT_SECONDS=120
   ```

4. Run the bot:

   ```bash
   python main.py
   ```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | Yes | Discord bot token. |
| `POST_CATEGORY_ID` | Yes for `!post` | Category where `!post` creates channels. |
| `POST_MODERATOR_ROLE_ID` | Yes for `!post` | Only users with this role ID can run `!post`. |
| `COMMAND_TIMEOUT_SECONDS` | No | Timeout for blocking data commands like `!price`, `!health`, `!rsa`. Default: `20`. |
| `CHART_TIMEOUT_SECONDS` | No | Timeout for chart generation in `!chart`. Default: `25`. |
| `TEST_ALL_TIMEOUT_SECONDS` | No | Timeout for `!test_all`. Default: `120`. |

## Command Reference

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

## `!post` Behavior

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

## Bot Help

Use `!help` to view the command overview and `!help <command>` for detailed usage/examples.

## Reliability Notes

- Keep the host awake. If the machine sleeps, Discord sessions are dropped and reconnected.
- Use stable network (prefer wired Ethernet for always-on bots).
- Run one token per bot process. Reusing the same token in multiple processes causes session churn.
- Use a process supervisor (`launchd`, `systemd`, `pm2`, or Docker restart policy) so crashes/restarts recover automatically.
- If logs show repeated "Can't keep up ... websocket is Xs behind", the host event loop is being starved or paused.

## Testing

Run tests with:

```bash
python -m unittest discover -q
```

## Open Source

**splitBot is open-source.**  
Repository: **<https://github.com/AlexanderRoller/splitBot>**
