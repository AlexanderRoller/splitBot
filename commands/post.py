import datetime as dt
import re


CLOCK_EMOJI = "\N{ALARM CLOCK}"
SUPPORTED_DATE_FORMATS_WITH_YEAR = (
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%m-%d-%Y",
    "%b-%d-%Y",
    "%b/%d/%Y",
    "%B-%d-%Y",
    "%b %d %Y",
    "%B %d %Y",
    "%b %d, %Y",
    "%B %d, %Y",
)
SUPPORTED_DATE_FORMATS_NO_YEAR = (
    "%m/%d",
    "%m-%d",
    "%b-%d",
    "%b/%d",
    "%B-%d",
    "%b %d",
    "%B %d",
)
SUPPORTED_DATE_FORMATS = SUPPORTED_DATE_FORMATS_WITH_YEAR + SUPPORTED_DATE_FORMATS_NO_YEAR


def parse_last_day_to_buy(value: str):
    raw_value = str(value or "").strip()
    if not raw_value:
        return None

    for date_format in SUPPORTED_DATE_FORMATS_WITH_YEAR:
        try:
            parsed = dt.datetime.strptime(raw_value, date_format)
            return parsed.date()
        except ValueError:
            continue

    current_year = dt.date.today().year
    for date_format in SUPPORTED_DATE_FORMATS_NO_YEAR:
        try:
            parsed = dt.datetime.strptime(
                f"{raw_value} {current_year}",
                f"{date_format} %Y",
            )
            return parsed.date()
        except ValueError:
            continue
    return None


def build_post_channel_name(ticker: str, buy_date):
    ticker_key = str(ticker or "").strip().upper()
    sanitized_ticker = re.sub(r"[^A-Z0-9]", "", ticker_key).lower()
    if not sanitized_ticker or buy_date is None:
        return None

    month_label = buy_date.strftime("%b").lower()
    day_label = str(buy_date.day)
    return f"{CLOCK_EMOJI}-{sanitized_ticker}-{month_label}-{day_label}"


def build_reverse_split_announcement(ticker: str, split_ratio: str, buy_date, source_link: str):
    ticker_key = str(ticker or "").strip().upper()
    split_ratio_value = str(split_ratio or "").strip()
    source_url = str(source_link or "").strip()
    buy_date_value = format_buy_date_short(buy_date)

    return (
        "@everyone\n"
        f"**Reverse Split Alert: {ticker_key}**\n"
        f"Split Ratio: {split_ratio_value}\n"
        f"Last Day to Buy: {buy_date_value}\n"
        f"Source: {source_url}"
    )


def format_buy_date_short(buy_date):
    return f"{buy_date.strftime('%b')} {buy_date.day}"


def has_post_permission(member, required_role_id):
    if required_role_id is None:
        return False

    roles = getattr(member, "roles", None) or []
    return any(getattr(role, "id", None) == required_role_id for role in roles)
