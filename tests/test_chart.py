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

    @patch("commands.chart.mpf", None)
    def test_missing_mplfinance_returns_error(self):
        _stream, _filename, _caption, error_message = chart.generate_stock_chart("AAPL", "1mo")
        self.assertIsNotNone(error_message)
        self.assertIn("Install mplfinance", error_message)

    @unittest.skipIf(chart.plt is None, "matplotlib not installed in test environment")
    @patch("commands.chart.get_ohlc_history", return_value=None)
    def test_missing_data_returns_error(self, _mock_history):
        _stream, _filename, _caption, error_message = chart.generate_stock_chart("AAPL", "1mo")
        self.assertIsNotNone(error_message)
        self.assertIn("Could not retrieve chart data", error_message)

    @unittest.skipIf(chart.plt is None or chart.mpf is None, "chart deps not installed in test environment")
    @patch("commands.chart.get_company_name", return_value="Apple Inc.")
    @patch("commands.chart.get_ohlc_history")
    def test_success_returns_png_stream(self, mock_history, _mock_company_name):
        import pandas as pd

        index = pd.to_datetime(
            [
                dt.datetime(2025, 1, 1),
                dt.datetime(2025, 1, 2),
                dt.datetime(2025, 1, 3),
            ]
        )
        frame = pd.DataFrame(
            {
                "Open": [100.0, 101.0, 102.0],
                "High": [102.0, 103.0, 104.0],
                "Low": [99.0, 100.0, 101.0],
                "Close": [101.0, 102.5, 101.0],
            },
            index=index,
        )
        mock_history.return_value = frame

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

    @unittest.skipIf(chart.plt is None or chart.mpf is None, "chart deps not installed in test environment")
    @patch("commands.chart.get_company_name", return_value="Apple Inc.")
    @patch("commands.chart.get_ohlc_history")
    def test_intraday_uses_time_in_xaxis_format(self, mock_history, _mock_company_name):
        import pandas as pd

        # Two points on the same date: x-axis must include time or all ticks look identical.
        index = pd.to_datetime([
            dt.datetime(2025, 2, 17, 9, 30),
            dt.datetime(2025, 2, 17, 10, 0),
        ])
        frame = pd.DataFrame(
            {
                "Open": [100.0, 101.0],
                "High": [102.0, 103.0],
                "Low": [99.0, 100.0],
                "Close": [100.0, 101.0],
            },
            index=index,
        )
        mock_history.return_value = frame

        with patch.object(chart.mpf, "plot", wraps=chart.mpf.plot) as wrapped_plot:
            stream, _filename, _caption, error_message = chart.generate_stock_chart("AAPL", "1d")
            try:
                self.assertIsNone(error_message)
                self.assertTrue(wrapped_plot.called)
                kwargs = wrapped_plot.call_args.kwargs
                self.assertEqual(kwargs.get("datetime_format"), "%H:%M")
            finally:
                if stream is not None:
                    stream.close()

    @unittest.skipIf(chart.plt is None or chart.mpf is None, "chart deps not installed in test environment")
    @patch("commands.chart.get_company_name", return_value="Apple Inc.")
    @patch("commands.chart.get_ohlc_history")
    def test_default_period_is_1d(self, mock_history, _mock_company_name):
        import pandas as pd

        index = pd.to_datetime([
            dt.datetime(2025, 1, 1),
            dt.datetime(2025, 1, 2),
        ])
        frame = pd.DataFrame(
            {
                "Open": [100.0, 101.0],
                "High": [102.0, 103.0],
                "Low": [99.0, 100.0],
                "Close": [100.0, 101.0],
            },
            index=index,
        )
        mock_history.return_value = frame

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
