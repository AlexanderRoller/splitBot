import yfinance as yf


def get_latest_price(ticker: str):
    stock = yf.Ticker(ticker)
    price = None

    try:
        fast_info = stock.fast_info
        if fast_info:
            price = (
                fast_info.get("last_price")
                or fast_info.get("lastPrice")
                or fast_info.get("last_close")
            )
    except Exception:
        price = None

    if price is None:
        try:
            info = stock.info or {}
            price = (
                info.get("currentPrice")
                or info.get("regularMarketPrice")
                or info.get("previousClose")
            )
        except Exception:
            price = None

    if price is None:
        try:
            history = stock.history(period="1d")
            if not history.empty:
                price = history["Close"].iloc[-1]
        except Exception:
            price = None

    return price
