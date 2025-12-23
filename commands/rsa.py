from commands.formatting import format_error, format_response
from commands.market_data import get_latest_price

def calculate_reverse_split_arbitrage(ticker: str, split_ratio: str):
    ticker_key = ticker.upper()
    current_price = get_latest_price(ticker_key)

    if current_price is None:
        return format_error(
            "Reverse Split Arbitrage",
            f"Could not retrieve the current price for ticker {ticker_key}.",
        )
    
    # Parse the reverse split ratio provided in the format 'numerator:denominator'
    try:
        split_parts = split_ratio.split(':')
        split_ratio_value = float(split_parts[0]) / float(split_parts[1])
    except (IndexError, ValueError):
        return format_error(
            "Reverse Split Arbitrage",
            "Invalid split ratio format. Use 'numerator:denominator'.",
        )
    
    # Calculate the profitability of the reverse split arbitrage
    profitability = float(current_price) * (split_ratio_value - 1)
    return format_response(
        f"Reverse Split Arbitrage for {ticker_key}",
        [
            f"Split Ratio: {split_ratio}",
            f"Estimated Profitability: ${profitability:.2f}",
        ],
    )
