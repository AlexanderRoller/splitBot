import io

from commands.formatting import format_error
from commands.market_data import get_company_name, get_ohlc_history

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except (ModuleNotFoundError, ImportError):
    plt = None

try:
    import mplfinance as mpf
except (ModuleNotFoundError, ImportError):
    mpf = None


PERIOD_TO_INTERVAL = {
    "1d": "5m",
    "5d": "15m",
    "1mo": "30m",
    "3mo": "1d",
    "6mo": "1d",
    "1y": "1d",
    "2y": "1d",
    "5y": "1wk",
    "max": "1mo",
}
DEFAULT_PERIOD = "1d"


def generate_stock_chart(ticker: str, period: str = DEFAULT_PERIOD):
    ticker_key = ticker.upper().strip()
    period_key = period.lower().strip()
    valid_periods = ", ".join(PERIOD_TO_INTERVAL.keys())

    if period_key not in PERIOD_TO_INTERVAL:
        return None, None, None, format_error(
            "Chart",
            f"Invalid period '{period}'. Valid periods: {valid_periods}",
        )

    if plt is None:
        return None, None, None, format_error(
            "Chart",
            "Chart rendering is unavailable. Install matplotlib.",
        )

    if mpf is None:
        return None, None, None, format_error(
            "Chart",
            "Chart rendering is unavailable. Install mplfinance.",
        )

    ohlc = get_ohlc_history(
        ticker_key,
        period=period_key,
        interval=PERIOD_TO_INTERVAL[period_key],
    )
    if ohlc is None or ohlc.empty:
        return None, None, None, format_error(
            "Chart",
            f"Could not retrieve chart data for ticker {ticker_key}.",
        )

    company_name = get_company_name(ticker_key)
    if company_name.strip().upper() == ticker_key:
        display_name = ticker_key
    else:
        display_name = f"{company_name} ({ticker_key})"

    figure = None
    try:
        close_prices = ohlc["Close"].astype(float).tolist()
        first_price = close_prices[0]
        last_price = close_prices[-1]
        change_amount = last_price - first_price
        change_percent = 0.0
        if first_price != 0:
            change_percent = (change_amount / first_price) * 100
        sign = "+" if change_amount >= 0 else "-"

        market_colors = mpf.make_marketcolors(
            up="#26a69a",
            down="#ef5350",
            edge={"up": "#26a69a", "down": "#ef5350"},
            wick={"up": "#26a69a", "down": "#ef5350"},
            volume="inherit",
        )
        style = mpf.make_mpf_style(
            base_mpf_style="nightclouds",
            marketcolors=market_colors,
            facecolor="#0D1117",
            figcolor="#0D1117",
            gridcolor="#30363D",
            gridstyle="--",
            rc={
                "axes.labelcolor": "#C9D1D9",
                "xtick.color": "#C9D1D9",
                "ytick.color": "#C9D1D9",
                "axes.edgecolor": "#30363D",
                "text.color": "#F0F6FC",
                "font.size": 10,
            },
        )

        interval = PERIOD_TO_INTERVAL[period_key]
        if interval.endswith("m") or interval.endswith("h"):
            # Intraday data needs time on the x-axis; otherwise every tick shows the same date.
            datetime_format = "%H:%M"
            if period_key != "1d":
                datetime_format = "%b %d %H:%M"
        elif interval.endswith("d") or interval.endswith("wk"):
            datetime_format = "%b %d"
        else:
            # Monthly-ish / fallback.
            datetime_format = "%Y-%m"

        figure, _axes = mpf.plot(
            ohlc,
            type="candle",
            style=style,
            volume=False,
            figsize=(10, 4.8),
            returnfig=True,
            xrotation=0,
            datetime_format=datetime_format,
            tight_layout=True,
            title=f"{display_name} ({period_key})",
        )

        caption = (
            f"**{display_name} Chart ({period_key})**\n"
            f"Last Price: ${last_price:.2f}\n"
            f"Change: {sign}${abs(change_amount):.2f} ({sign}{abs(change_percent):.2f}%)"
        )

        image_stream = io.BytesIO()
        figure.savefig(
            image_stream,
            format="png",
            dpi=150,
            facecolor=figure.get_facecolor(),
            bbox_inches="tight",
        )
        image_stream.seek(0)
        filename = f"{ticker_key}_{period_key}_dark_chart.png"
        return image_stream, filename, caption, None
    except Exception:
        return None, None, None, format_error(
            "Chart",
            f"Could not build chart for ticker {ticker_key}.",
        )
    finally:
        if figure is not None:
            plt.close(figure)
