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


def get_price_snapshot(ticker: str):
    stock = yf.Ticker(ticker)
    last_price = None
    previous_close = None

    try:
        fast_info = stock.fast_info or {}
        last_price = (
            fast_info.get("last_price")
            or fast_info.get("lastPrice")
            or fast_info.get("last_close")
        )
        previous_close = (
            fast_info.get("previous_close")
            or fast_info.get("previousClose")
        )
        if previous_close is None:
            previous_close = fast_info.get("last_close")
    except Exception:
        last_price = None
        previous_close = None

    if last_price is None or previous_close is None:
        try:
            info = stock.info or {}
            if last_price is None:
                last_price = (
                    info.get("currentPrice")
                    or info.get("regularMarketPrice")
                )
            if previous_close is None:
                previous_close = (
                    info.get("previousClose")
                    or info.get("regularMarketPreviousClose")
                )
        except Exception:
            pass

    if last_price is None or previous_close is None:
        try:
            history = stock.history(period="2d")
            if not history.empty:
                if last_price is None:
                    last_price = history["Close"].iloc[-1]
                if previous_close is None and len(history) > 1:
                    previous_close = history["Close"].iloc[-2]
        except Exception:
            pass

    return last_price, previous_close
