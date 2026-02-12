try:
    import yfinance as yf
except ModuleNotFoundError:
    yf = None


def _get_stock(ticker: str):
    if yf is None:
        return None
    return yf.Ticker(ticker)


def get_latest_price(ticker: str):
    stock = _get_stock(ticker)
    if stock is None:
        return None

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
    stock = _get_stock(ticker)
    if stock is None:
        return None, None

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


def get_price_history(ticker: str, period: str = "3mo", interval: str = "1d"):
    stock = _get_stock(ticker)
    if stock is None:
        return None, None

    try:
        history = stock.history(period=period, interval=interval)
        if history is None or history.empty:
            return None, None

        close_values = history["Close"].dropna()
        if close_values.empty:
            return None, None

        timestamps = close_values.index.to_pydatetime().tolist()
        prices = [float(value) for value in close_values.tolist()]
        if not timestamps or not prices:
            return None, None
        return timestamps, prices
    except Exception:
        return None, None


def get_company_name(ticker: str):
    ticker_key = ticker.upper().strip()
    stock = _get_stock(ticker_key)
    if stock is None:
        return ticker_key

    try:
        info = stock.info or {}
        company_name = (
            info.get("longName")
            or info.get("shortName")
            or info.get("displayName")
            or info.get("name")
        )
        if company_name:
            cleaned_name = str(company_name).strip()
            if cleaned_name:
                return cleaned_name
    except Exception:
        pass

    return ticker_key
