import io

from commands.formatting import format_error
from commands.market_data import get_company_name, get_price_history

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except (ModuleNotFoundError, ImportError):
    plt = None


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

    timestamps, prices = get_price_history(
        ticker_key,
        period=period_key,
        interval=PERIOD_TO_INTERVAL[period_key],
    )
    if not timestamps or not prices:
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
        figure, axis = plt.subplots(figsize=(10, 4.8))
        figure.patch.set_facecolor("#0D1117")
        axis.set_facecolor("#161B22")

        axis.plot(timestamps, prices, color="#58A6FF", linewidth=2.2)
        axis.fill_between(timestamps, prices, min(prices), color="#1F6FEB", alpha=0.22)
        axis.grid(True, color="#30363D", linestyle="--", linewidth=0.7, alpha=0.5)

        for spine in axis.spines.values():
            spine.set_color("#30363D")

        axis.tick_params(colors="#C9D1D9")
        axis.set_title(f"{display_name} Price Chart ({period_key})", color="#F0F6FC", pad=12)
        axis.set_ylabel("Price (USD)", color="#C9D1D9")
        figure.autofmt_xdate()

        first_price = prices[0]
        last_price = prices[-1]
        change_amount = last_price - first_price
        change_percent = 0.0
        if first_price != 0:
            change_percent = (change_amount / first_price) * 100
        sign = "+" if change_amount >= 0 else "-"

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
