import unittest
from unittest.mock import patch

from commands.rsa import calculate_reverse_split_arbitrage


class ReverseSplitArbitrageTests(unittest.TestCase):
    @patch("commands.rsa.get_latest_price", return_value=10.0)
    def test_valid_ratio_returns_profitability(self, _mock_price):
        response = calculate_reverse_split_arbitrage("aapl", "2:1")
        self.assertIn("**Reverse Split Arbitrage for AAPL**", response)
        self.assertIn("Estimated Profitability: $10.00", response)

    @patch("commands.rsa.get_latest_price", return_value=10.0)
    def test_zero_denominator_returns_error(self, _mock_price):
        response = calculate_reverse_split_arbitrage("AAPL", "2:0")
        self.assertIn("**Reverse Split Arbitrage Error**", response)
        self.assertIn("Denominator cannot be zero", response)

    @patch("commands.rsa.get_latest_price", return_value=10.0)
    def test_invalid_ratio_format_returns_error(self, _mock_price):
        response = calculate_reverse_split_arbitrage("AAPL", "2")
        self.assertIn("**Reverse Split Arbitrage Error**", response)
        self.assertIn("Use 'numerator:denominator'", response)

    @patch("commands.rsa.get_latest_price", return_value=None)
    def test_missing_price_returns_error(self, _mock_price):
        response = calculate_reverse_split_arbitrage("AAPL", "2:1")
        self.assertIn("Could not retrieve the current price", response)


if __name__ == "__main__":
    unittest.main()
