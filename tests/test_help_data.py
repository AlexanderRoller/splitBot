import unittest

from commands.help_data import (
    HELP_COMMANDS,
    HELP_ORDER,
    build_command_help_lines,
    build_help_overview_lines,
    normalize_help_command_name,
)


class HelpDataTests(unittest.TestCase):
    def test_every_help_entry_has_examples(self):
        for command_name in HELP_ORDER:
            entry = HELP_COMMANDS[command_name]
            self.assertTrue(entry.get("examples"))

    def test_normalize_help_command_name(self):
        self.assertEqual(normalize_help_command_name("price"), "price")
        self.assertEqual(normalize_help_command_name("!chart"), "chart")
        self.assertEqual(normalize_help_command_name("  !PoSt  "), "post")

    def test_build_help_overview_lines_contains_examples(self):
        lines = build_help_overview_lines()
        self.assertTrue(any(line.startswith("Example: `!") for line in lines))
        self.assertTrue(any("!help [command]" in line for line in lines))

    def test_build_command_help_lines_for_valid_command(self):
        name, lines = build_command_help_lines("chart")
        self.assertEqual(name, "chart")
        self.assertTrue(any(line.startswith("Usage: `!chart") for line in lines))
        self.assertTrue(any(line.startswith("Examples:") for line in lines))
        self.assertTrue(any(line.startswith("`!chart ") or line == "`!chart TSLA`" for line in lines))

    def test_build_command_help_lines_for_unknown_command(self):
        name, lines = build_command_help_lines("unknown")
        self.assertIsNone(name)
        self.assertIsNone(lines)


if __name__ == "__main__":
    unittest.main()
