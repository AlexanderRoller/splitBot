from commands.formatting import format_error, format_response
from commands.market_data import get_latest_price

def get_stock_price(ticker: str):
    ticker_key = ticker.upper()
    last_price = get_latest_price(ticker_key)

    if last_price is not None:
        response = format_response(
            f"Price for {ticker_key}",
            [f"Last Price: ${float(last_price):.2f}"],
        )
    else:
        response = format_error(
            "Price Lookup",
            f"Could not retrieve the last price for ticker {ticker_key}.",
        )
    
    return response
