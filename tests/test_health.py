import unittest
from unittest.mock import patch

import commands.health as health


class ServerHealthTests(unittest.TestCase):
    def test_missing_psutil_falls_back_to_unavailable(self):
        with patch("commands.health.psutil", None):
            response = health.get_server_status()
        self.assertIn("**Server Health**", response)
        self.assertIn("CPU Usage: Unavailable", response)
        self.assertIn("CPU Temperature: Unavailable", response)

    @unittest.skipIf(health.psutil is None, "psutil not installed in test environment")
    @patch("commands.health.psutil.disk_usage")
    @patch("commands.health.psutil.boot_time")
    @patch("commands.health.psutil.virtual_memory")
    @patch("commands.health.psutil.cpu_percent")
    @patch("commands.health.open", side_effect=PermissionError)
    def test_temp_permission_error_falls_back_to_unavailable(
        self,
        _mock_open,
        mock_cpu_percent,
        mock_virtual_memory,
        mock_boot_time,
        mock_disk_usage,
    ):
        mock_cpu_percent.return_value = 12.3
        mock_virtual_memory.return_value = type("vm", (), {"percent": 45.6})()
        mock_boot_time.return_value = 1000.0
        mock_disk_usage.return_value = type("du", (), {"percent": 78.9})()

        with patch("commands.health.time.time", return_value=2000.0):
            response = health.get_server_status()

        self.assertIn("**Server Health**", response)
        self.assertIn("CPU Temperature: Unavailable", response)


if __name__ == "__main__":
    unittest.main()
