from commands.formatting import format_error, format_response
from commands.market_data import get_price_snapshot

def get_stock_price(ticker: str):
    ticker_key = ticker.upper()
    last_price, previous_close = get_price_snapshot(ticker_key)

    if last_price is not None:
        lines = [f"Last Price: ${float(last_price):.2f}"]
        if previous_close is not None and float(previous_close) != 0.0:
            change_amount = float(last_price) - float(previous_close)
            change_percent = (change_amount / float(previous_close)) * 100
            sign = "+" if change_amount >= 0 else "-"
            lines.append(
                f"Daily Change: {sign}${abs(change_amount):.2f} ({sign}{abs(change_percent):.2f}%)"
            )
        else:
            lines.append("Daily Change: unavailable")
        response = format_response(
            f"Price for {ticker_key}",
            lines,
        )
    else:
        response = format_error(
            "Price Lookup",
            f"Could not retrieve the last price for ticker {ticker_key}.",
        )
    
    return response
