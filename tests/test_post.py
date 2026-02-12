import datetime as dt
import unittest

from commands.post import (
    CLOCK_EMOJI,
    build_post_channel_name,
    build_reverse_split_announcement,
    format_buy_date_short,
    has_post_permission,
    parse_last_day_to_buy,
)


class DummyRole:
    def __init__(self, role_id, name):
        self.id = role_id
        self.name = name


class DummyMember:
    def __init__(self, roles):
        self.roles = roles


class PostCommandHelperTests(unittest.TestCase):
    def test_parse_last_day_to_buy_supports_multiple_formats(self):
        self.assertEqual(parse_last_day_to_buy("2026-02-12"), dt.date(2026, 2, 12))
        self.assertEqual(parse_last_day_to_buy("02/12/2026"), dt.date(2026, 2, 12))
        self.assertEqual(parse_last_day_to_buy("Feb-12-2026"), dt.date(2026, 2, 12))
        self.assertEqual(parse_last_day_to_buy("February 12, 2026"), dt.date(2026, 2, 12))
        self.assertEqual(parse_last_day_to_buy("02/12").month, 2)
        self.assertEqual(parse_last_day_to_buy("Feb-12").day, 12)

    def test_parse_last_day_to_buy_invalid_value_returns_none(self):
        self.assertIsNone(parse_last_day_to_buy("not-a-date"))

    def test_build_post_channel_name_uses_required_format(self):
        buy_date = dt.date(2026, 2, 7)
        channel_name = build_post_channel_name("AAPL", buy_date)
        self.assertEqual(channel_name, f"{CLOCK_EMOJI}-aapl-feb-7")

    def test_build_reverse_split_announcement_contains_everything(self):
        buy_date = dt.date(2026, 2, 12)
        message = build_reverse_split_announcement(
            "AAPL",
            "1:10",
            buy_date,
            "https://example.com/source",
        )
        self.assertIn("@everyone", message)
        self.assertIn("Reverse Split Alert: AAPL", message)
        self.assertIn("Split Ratio: 1:10", message)
        self.assertIn("Last Day to Buy: Feb 12", message)
        self.assertIn("Source: https://example.com/source", message)

    def test_format_buy_date_short_uses_month_day(self):
        buy_date = dt.date(2026, 2, 5)
        self.assertEqual(format_buy_date_short(buy_date), "Feb 5")

    def test_has_post_permission_requires_role_id(self):
        member = DummyMember([DummyRole(1, "member"), DummyRole(2, "Moderator")])
        self.assertFalse(has_post_permission(member, required_role_id=None))

    def test_has_post_permission_by_role_id(self):
        member = DummyMember([DummyRole(99, "something"), DummyRole(12345, "whatever")])
        self.assertTrue(has_post_permission(member, 12345))
        self.assertFalse(has_post_permission(member, 333))


if __name__ == "__main__":
    unittest.main()
