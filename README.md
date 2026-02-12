# BurryDeez Discord Bot

This Discord bot provides lightweight financial utilities to help users stay informed about the stock market. It offers live stock price lookups, dark mode stock charts, reverse split arbitrage estimates, server health insights, and a quick user count command.

## Features

- **📈 Live Stock Price Fetching**: Retrieve the most up-to-date stock prices during market hours, or the last available price after hours using the `yfinance` API.
- **📉 Dark Mode Stock Charts**: Generate and post dark-themed stock charts directly in Discord.
- **🔁 Reverse Split Arbitrage**: Estimate profitability based on a specified reverse split ratio and the latest market price.
- **🖥️ Server Health Monitoring**: Track CPU usage, memory usage, disk usage, uptime, and component temperatures.
- **👥 User Count**: Return the number of users currently in the Discord server.

---

## Prerequisites

Before using the bot, ensure you have the following installed:

- **Python 3.6 or higher**
- **Discord API Token**: You'll need to create a bot on the [Discord Developer Portal](https://discord.com/developers/applications) and get a token.
- **Dependencies**:
  - `discord.py`: Connect to Discord and handle commands.
  - `yfinance`: Fetch market prices from a free data source.
  - `psutil`: Monitor system performance for server health checks.
  - `python-dotenv`: Load environment variables from the `.env` file.
  - `matplotlib`: Render stock charts as images.

---

## Setup

To get started, follow these steps:

### 1. **Clone the Repository**
   First, clone the repository from GitHub to your local machine:
   ```bash
   git clone https://github.com/AlexanderRoller/BurryDeez.git
   ```

### 2. **Install Dependencies**
   Navigate to the project directory and install all required dependencies using the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

### 3. **Configuration**

   Before running the bot, create a `.env` file in the root directory of the project. This file stores sensitive information like your Discord bot token. Use the format below:

   ```plaintext
   BOT_TOKEN=your_discord_bot_token
   ```

   - **BOT_TOKEN**: The token for your Discord bot.

---

## Usage

Once everything is set up, you can start the bot with the following command:

```bash
python main.py
```

The bot will immediately connect to Discord and respond to commands in your server.

---

## Commands

Here are the available commands you can use with the bot:

- **`!price [ticker]`**
  - **Description**: Fetch the current or most recent stock price plus the daily change in dollars and percent.
  - **Example**: `!price AAPL`

- **`!chart [ticker] [period]`**
  - **Description**: Generate a dark mode price chart image for a ticker. Period is optional (default `1d`).
  - **Valid Periods**: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `max`
  - **Example**: `!chart TSLA 6mo`

- **`!rsa [ticker] [split ratio]`**
  - **Description**: Estimate the profitability of reverse split arbitrage.
  - **Example**: `!rsa AAPL 2:1`

- **`!health`**
  - **Description**: Display server health status (CPU, memory, disk, uptime, temperature).
  - **Example**: `!health`

- **`!usercount`**
  - **Description**: Return the total number of members in the Discord server.
  - **Example**: `!usercount`

- **`!test_all`**
  - **Description**: Run a quick set of command checks with sample inputs.
  - **Example**: `!test_all`

---

## Contributing

Contributions to this project are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b my-new-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin my-new-feature`).
5. Create a Pull Request, and we will review it!

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
