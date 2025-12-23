import datetime as dt
import json
import os
import re

import requests
from bs4 import BeautifulSoup

from commands.formatting import format_error, format_response

CALENDAR_URLS = [
    "https://www.marketwatch.com/tools/calendars/economic",
    "https://www.marketwatch.com/economy-politics/calendar",
    "https://www.marketwatch.com/tools/calendars/economic?mod=top_nav",
    "https://www.marketwatch.com/economy-politics/calendar?mod=top_nav",
]
BASE_URL = "https://www.marketwatch.com"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}
MAX_EVENTS_PER_DAY = 6
MAX_MESSAGE_LENGTH = 1800


def get_week_start(today=None):
    if today is None:
        today = dt.date.today()
    return today - dt.timedelta(days=today.weekday())


def get_week_end(week_start):
    return week_start + dt.timedelta(days=6)


def summarize_weekly_calendar(include_command=False, title_prefix="Economic Calendar"):
    html, source_url, error = _fetch_calendar_html()
    if not html:
        detail = f"Could not reach MarketWatch ({error})."
        if error and "401" in str(error):
            detail += " MarketWatch blocked the request; set MARKETWATCH_COOKIE if needed."
        return format_error("Economic Calendar", detail)

    events = _extract_events(html)
    if not events:
        return format_error(
            "Economic Calendar",
            "No events found. MarketWatch layout may have changed.",
        )

    week_start = get_week_start()
    week_end = get_week_end(week_start)
    week_events = [
        event
        for event in events
        if event.get("date") and week_start <= event["date"] <= week_end
    ]
    if not week_events:
        week_events = events

    title = f"{title_prefix} (Week of {week_start.strftime('%Y-%m-%d')})"
    if include_command:
        title += " (!calendar)"

    lines = _build_week_lines(week_events, MAX_EVENTS_PER_DAY)
    message = format_response(title, lines, footer=f"Source: MarketWatch ({source_url})")

    if len(message) > MAX_MESSAGE_LENGTH:
        lines = _build_week_lines(week_events, 3)
        message = format_response(title, lines, footer=f"Source: MarketWatch ({source_url})")

    if len(message) > MAX_MESSAGE_LENGTH:
        lines = _build_week_lines(week_events, 1)
        message = format_response(title, lines, footer=f"Source: MarketWatch ({source_url})")

    if len(message) > MAX_MESSAGE_LENGTH:
        message = message[: MAX_MESSAGE_LENGTH - 3] + "..."

    return message


def _fetch_calendar_html():
    last_error = "Unknown error"
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)
    cookie = os.getenv("MARKETWATCH_COOKIE")
    if cookie:
        session.headers["Cookie"] = cookie

    try:
        session.get(BASE_URL, timeout=10)
    except requests.RequestException as exc:
        last_error = str(exc)

    for url in CALENDAR_URLS:
        try:
            response = session.get(
                url,
                headers={"Referer": BASE_URL},
                timeout=15,
            )
            if response.ok and response.text:
                return response.text, url, None
            last_error = f"HTTP {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)
    return None, None, last_error


def _build_week_lines(events, max_events_per_day):
    grouped = {}
    for event in events:
        grouped.setdefault(event["date"], []).append(event)

    lines = []
    for day in sorted(grouped.keys()):
        day_events = sorted(
            grouped[day],
            key=lambda item: (_time_sort_key(item.get("time")), item.get("title", "")),
        )
        summaries = [_format_event_summary(event) for event in day_events]

        remaining = 0
        if len(summaries) > max_events_per_day:
            remaining = len(summaries) - max_events_per_day
            summaries = summaries[:max_events_per_day]

        line = f"{day.strftime('%a %m/%d')}: " + "; ".join(summaries)
        if remaining:
            line += f"; +{remaining} more"
        lines.append(_truncate_line(line, 320))

    return lines


def _truncate_line(text, max_length):
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def _format_event_summary(event):
    title = event.get("title", "Unknown Event")
    time_value = event.get("time")
    country = event.get("country")
    impact = event.get("impact")

    label = title
    if time_value:
        label = f"{time_value} - {label}"

    details = ", ".join(part for part in [country, impact] if part)
    if details:
        label += f" ({details})"
    return label


def _time_sort_key(time_value):
    if not time_value:
        return (1, 0)
    lower = time_value.lower()
    if "all day" in lower or "tentative" in lower:
        return (1, 0)
    match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*([ap]m)", lower)
    if not match:
        return (1, 0)
    hour = int(match.group(1)) % 12
    minute = int(match.group(2) or 0)
    if match.group(3) == "pm":
        hour += 12
    return (0, hour * 60 + minute)


def _extract_events(html):
    soup = BeautifulSoup(html, "html.parser")
    events = _extract_events_from_scripts(soup)
    if not events:
        events = _extract_events_from_tables(soup)
    return _dedupe_events(events)


def _dedupe_events(events):
    seen = set()
    unique = []
    for event in events:
        key = (
            event.get("title"),
            event.get("date"),
            event.get("time"),
            event.get("country"),
            event.get("impact"),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(event)
    return unique


def _extract_events_from_scripts(soup):
    for script in soup.find_all("script"):
        text = script.string or script.get_text()
        if not text:
            continue
        if "calendar" not in text.lower() and "economic" not in text.lower():
            continue
        for blob in _extract_json_blobs(text):
            events = _find_events_in_data(blob)
            if events:
                return events
    return []


def _extract_json_blobs(text):
    blobs = []
    stripped = text.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            blobs.append(json.loads(stripped))
        except json.JSONDecodeError:
            pass

    match = re.search(r"__NEXT_DATA__\"[^>]*>(.*?)</script>", text, re.S)
    if match:
        try:
            blobs.append(json.loads(match.group(1)))
        except json.JSONDecodeError:
            pass

    assign_match = re.search(r"=\s*({.*});", text, re.S)
    if assign_match:
        try:
            blobs.append(json.loads(assign_match.group(1)))
        except json.JSONDecodeError:
            pass

    return blobs


def _find_events_in_data(data):
    events = []
    if isinstance(data, dict):
        if _looks_like_event(data):
            event = _normalize_event_data(data)
            if event:
                events.append(event)
        for value in data.values():
            events.extend(_find_events_in_data(value))
    elif isinstance(data, list):
        for item in data:
            events.extend(_find_events_in_data(item))
    return events


def _looks_like_event(data):
    title_keys = {"event", "eventName", "eventTitle", "title", "name", "report"}
    date_keys = {
        "date",
        "eventDate",
        "releaseDate",
        "startDate",
        "startTime",
        "dateTime",
        "timestamp",
        "time",
    }
    return bool(title_keys.intersection(data.keys()) and date_keys.intersection(data.keys()))


def _normalize_event_data(data):
    title = _first_value(
        data,
        ["eventName", "eventTitle", "event", "title", "name", "report"],
    )
    if not title:
        return None

    date_value = _first_value(
        data,
        ["eventDate", "releaseDate", "startDate", "date", "dateTime", "timestamp"],
    )
    event_date, event_time = _parse_date_time(date_value)
    if not event_date:
        return None

    time_value = _first_value(data, ["time", "startTime"])
    if time_value and not event_time:
        event_time = _normalize_time_string(time_value)

    return {
        "title": str(title).strip(),
        "date": event_date,
        "time": event_time,
        "country": _normalize_value(_first_value(data, ["country", "region", "currency"])),
        "impact": _normalize_value(_first_value(data, ["importance", "impact"])),
    }


def _extract_events_from_tables(soup):
    events = []
    for table in soup.find_all("table"):
        header_cells = []
        thead = table.find("thead")
        if thead:
            header_cells = thead.find_all("th")
        if not header_cells:
            first_row = table.find("tr")
            if first_row:
                header_cells = first_row.find_all("th")

        headers = [th.get_text(" ", strip=True).lower() for th in header_cells]
        if not headers:
            continue
        if not any("event" in header or "report" in header for header in headers):
            continue

        idx_event = _find_header_index(headers, ["event", "report", "description"])
        idx_time = _find_header_index(headers, ["time"])
        idx_date = _find_header_index(headers, ["date"])
        idx_country = _find_header_index(headers, ["country"])
        idx_impact = _find_header_index(headers, ["impact", "importance"])

        current_date = None
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            row_text = " ".join(cell.get_text(" ", strip=True) for cell in cells)
            parsed_date = _parse_date(row_text)
            if len(cells) == 1 and parsed_date:
                current_date = parsed_date
                continue

            cell_texts = [cell.get_text(" ", strip=True) for cell in cells]
            title = _get_cell(cell_texts, idx_event)
            if not title:
                continue

            date_value = _get_cell(cell_texts, idx_date)
            event_date = _parse_date(date_value) if date_value else None
            if not event_date:
                event_date = current_date
            if not event_date:
                continue

            events.append(
                {
                    "title": title,
                    "date": event_date,
                    "time": _normalize_time_string(_get_cell(cell_texts, idx_time)),
                    "country": _normalize_value(_get_cell(cell_texts, idx_country)),
                    "impact": _normalize_value(_get_cell(cell_texts, idx_impact)),
                }
            )

    return events


def _find_header_index(headers, keywords):
    for index, header in enumerate(headers):
        if any(keyword in header for keyword in keywords):
            return index
    return None


def _get_cell(cells, index):
    if index is None or index >= len(cells):
        return None
    value = cells[index].strip()
    return value or None


def _first_value(data, keys):
    for key in keys:
        value = data.get(key)
        if value is not None and value != "":
            return value
    return None


def _normalize_value(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        joined = ", ".join(str(item).strip() for item in value if item)
        return joined or None
    text = str(value).strip()
    return text or None


def _parse_date_time(value):
    if value is None:
        return None, None

    if isinstance(value, (int, float)):
        timestamp = float(value)
        if timestamp > 1e12:
            timestamp /= 1000
        try:
            dt_value = dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc)
            return dt_value.date(), dt_value.strftime("%I:%M %p").lstrip("0")
        except (ValueError, OSError):
            return None, None

    text = str(value).strip()
    if not text:
        return None, None

    iso_value = text.replace("Z", "+00:00")
    if hasattr(dt.datetime, "fromisoformat"):
        try:
            dt_value = dt.datetime.fromisoformat(iso_value)
            return dt_value.date(), dt_value.strftime("%I:%M %p").lstrip("0")
        except ValueError:
            pass

    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt_value = dt.datetime.strptime(iso_value, fmt)
            return dt_value.date(), dt_value.strftime("%I:%M %p").lstrip("0")
        except ValueError:
            continue

    date_only = _parse_date(text)
    if date_only:
        return date_only, None

    return None, None


def _parse_date(text):
    if not text:
        return None

    cleaned = re.sub(r"\s+", " ", text).strip()
    lower = cleaned.lower()
    today = dt.date.today()

    if lower == "today":
        return today
    if lower == "tomorrow":
        return today + dt.timedelta(days=1)

    cleaned = re.sub(r"[^a-zA-Z0-9,/\- ]", "", cleaned).strip()
    formats = [
        "%A, %B %d, %Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%B %d",
        "%b %d",
        "%m/%d",
    ]
    for fmt in formats:
        try:
            parsed = dt.datetime.strptime(cleaned, fmt)
            if "%Y" not in fmt and "%y" not in fmt:
                parsed = parsed.replace(year=today.year)
            return parsed.date()
        except ValueError:
            continue
    return None


def _normalize_time_string(value):
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = re.sub(r"\s+", " ", text)
    match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*([ap]m)", text.lower())
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        suffix = match.group(3).upper()
        return f"{hour}:{minute:02d} {suffix}"
    return text
