import datetime as dt
import unittest
from unittest.mock import patch

import commands.chart as chart


class StockChartTests(unittest.TestCase):
    def test_invalid_period_returns_error(self):
        _stream, _filename, _caption, error_message = chart.generate_stock_chart("AAPL", "bad")
        self.assertIsNotNone(error_message)
        self.assertIn("**Chart Error**", error_message)
        self.assertIn("Invalid period", error_message)

    @patch("commands.chart.plt", None)
    def test_missing_matplotlib_returns_error(self):
        _stream, _filename, _caption, error_message = chart.generate_stock_chart("AAPL", "1mo")
        self.assertIsNotNone(error_message)
        self.assertIn("Install matplotlib", error_message)

    @unittest.skipIf(chart.plt is None, "matplotlib not installed in test environment")
    @patch("commands.chart.get_price_history", return_value=(None, None))
    def test_missing_data_returns_error(self, _mock_history):
        _stream, _filename, _caption, error_message = chart.generate_stock_chart("AAPL", "1mo")
        self.assertIsNotNone(error_message)
        self.assertIn("Could not retrieve chart data", error_message)

    @unittest.skipIf(chart.plt is None, "matplotlib not installed in test environment")
    @patch("commands.chart.get_company_name", return_value="Apple Inc.")
    @patch("commands.chart.get_price_history")
    def test_success_returns_png_stream(self, mock_history, _mock_company_name):
        timestamps = [
            dt.datetime(2025, 1, 1),
            dt.datetime(2025, 1, 2),
            dt.datetime(2025, 1, 3),
        ]
        prices = [100.0, 102.5, 101.0]
        mock_history.return_value = (timestamps, prices)

        stream, filename, caption, error_message = chart.generate_stock_chart("AAPL", "1mo")
        try:
            self.assertIsNone(error_message)
            self.assertIsNotNone(stream)
            self.assertEqual(filename, "AAPL_1mo_dark_chart.png")
            self.assertIn("**Apple Inc. (AAPL) Chart (1mo)**", caption)
            self.assertTrue(stream.getvalue().startswith(b"\x89PNG\r\n\x1a\n"))
        finally:
            if stream is not None:
                stream.close()

    @unittest.skipIf(chart.plt is None, "matplotlib not installed in test environment")
    @patch("commands.chart.get_company_name", return_value="Apple Inc.")
    @patch("commands.chart.get_price_history")
    def test_default_period_is_1d(self, mock_history, _mock_company_name):
        timestamps = [
            dt.datetime(2025, 1, 1),
            dt.datetime(2025, 1, 2),
        ]
        prices = [100.0, 101.0]
        mock_history.return_value = (timestamps, prices)

        stream, _filename, _caption, error_message = chart.generate_stock_chart("AAPL")
        try:
            self.assertIsNone(error_message)
            mock_history.assert_called_once_with(
                "AAPL",
                period="1d",
                interval=chart.PERIOD_TO_INTERVAL["1d"],
            )
        finally:
            if stream is not None:
                stream.close()


if __name__ == "__main__":
    unittest.main()
