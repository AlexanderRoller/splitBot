# BurryDeez Discord Bot

BurryDeez is a Discord bot for quick stock utilities, chart snapshots, reverse split workflows, and basic server diagnostics.

## Features

- `!price`: live/recent stock price + daily change
- `!chart`: dark mode chart image for a ticker
- `!rsa`: reverse split arbitrage estimate
- `!post`: moderator-only reverse split channel creation + announcement
- `!health`: server health summary
- `!usercount`: total member count
- `!help`: instruction message + command-specific help

## Requirements

- Python 3.8+
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
   git clone https://github.com/AlexanderRoller/BurryDeez.git
   cd BurryDeez
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

## Bot Instructions Message

Running `!help` posts the full welcome/instructions message with examples for every command.
Running `!help <command>` shows command-specific usage, details, and examples.

## Testing

Run tests with:

```bash
python -m unittest discover -q
```

## Open Source

**Burry Deez Bot is open-source.**  
Repository: **[Burry Deez GitHub](https://github.com/AlexanderRoller/BurryDeez)**
