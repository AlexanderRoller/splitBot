from commands.formatting import format_error, format_response
from commands.market_data import get_latest_price


def _parse_split_ratio(split_ratio: str):
    split_parts = [part.strip() for part in split_ratio.split(":")]
    if len(split_parts) != 2:
        raise ValueError

    numerator = float(split_parts[0])
    denominator = float(split_parts[1])

    if denominator == 0:
        raise ZeroDivisionError
    if numerator <= 0 or denominator <= 0:
        raise ValueError
    if numerator >= denominator:
        raise ValueError

    # Reverse split ratios are expected in small:big format (e.g., 1:10).
    return denominator / numerator


def calculate_reverse_split_arbitrage(ticker: str, split_ratio: str):
    ticker_key = ticker.upper()
    current_price = get_latest_price(ticker_key)

    if current_price is None:
        return format_error(
            "Reverse Split Arbitrage",
            f"Could not retrieve the current price for ticker {ticker_key}.",
        )

    try:
        split_ratio_value = _parse_split_ratio(split_ratio)
    except ZeroDivisionError:
        return format_error(
            "Reverse Split Arbitrage",
            "Invalid split ratio format. Denominator cannot be zero.",
        )
    except ValueError:
        return format_error(
            "Reverse Split Arbitrage",
            "Invalid split ratio format. Use 'small:big' with positive numbers (example: 1:10).",
        )

    profitability = float(current_price) * (split_ratio_value - 1)
    return format_response(
        f"Reverse Split Arbitrage for {ticker_key}",
        [
            f"Split Ratio: {split_ratio}",
            f"Estimated Profitability: ${profitability:.2f}",
        ],
    )
