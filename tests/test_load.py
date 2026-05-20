import unittest
import sys
from unittest.mock import patch, MagicMock
import asyncio
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
# Add the project root to the system path
sys.path.append('.')

from pyload import Loadtester

class TestLoadTesterReadErrorCases(unittest.TestCase):
    """Unit tests for error cases in the read() method"""

    def setUp(self):
        """Set up test fixtures"""
        self.tester = Loadtester()

    # ===== MISSING REQUIRED ARGUMENTS =====

    @patch('sys.argv', ['script.py'])
    def test_missing_ccload_positional(self):
        """Test error when ccload positional argument is missing"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py'])
    def test_missing_all_args(self):
        """Test error when no args are provided"""
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== HISTORY MODE WITH CONFLICTING ARGS =====

    @patch('sys.argv', ['script.py', 'httpbin.org', '-history'])
    def test_history_and_url_together(self):
        """Test error when URL and -history are used together"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'httpbin.org', '-GET', '-POST'])
    def test_multiple_http_methods(self):
        """Test error when multiple HTTP methods are used together"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'httpbin.org', '-GET', '-PUT'])
    def test_get_and_put_together(self):
        """Test error when GET and PUT are used together"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'httpbin.org', '-POST', '-DELETE'])
    def test_post_and_delete_together(self):
        """Test error when POST and DELETE are used together"""
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== METHOD FLAG VALIDATION =====

    @patch('sys.argv', ['script.py', 'httpbin.org'])
    def test_url_without_method_flag(self):
        """Test that URL works without explicit method flag (falls back to env/default)"""
        with patch('pyload.Loadtester.testurl') as mock_testurl:
            self.tester.read()
            mock_testurl.assert_called_once()

    # ===== HISTORY MODE WITH CONFLICTING ARGS =====

    @patch('sys.argv', ['script.py', 'httpbin.org', '-history'])
    def test_history_with_url(self):
        """Test error when -history is used with a URL"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', '-history', '-GET'])
    def test_history_with_get_method(self):
        """Test error when -history is used with -GET"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', '-history', '-POST'])
    def test_history_with_post_method(self):
        """Test error when -history is used with -POST"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', '-history', '-PUT'])
    def test_history_with_put_method(self):
        """Test error when -history is used with -PUT"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', '-history', '-DELETE'])
    def test_history_with_delete_method(self):
        """Test error when -history is used with -DELETE"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', '-history', '-PATCH'])
    def test_history_with_patch_method(self):
        """Test error when -history is used with -PATCH"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'httpbin.org', '-history'])
    def test_history_with_url_and_method(self):
        """Test error when -history is used with URL and method"""
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== INVALID JSON DATA =====

    @patch('sys.argv', ['script.py', 'httpbin.org', '-POST', '-d', 'invalid json'])
    def test_invalid_json_in_post(self):
        """Test error when POST data is not valid JSON"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'httpbin.org', '-PUT', '-d', '{invalid}'])
    def test_invalid_json_in_put(self):
        """Test error when PUT data is not valid JSON"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'httpbin.org', '-DELETE', '-d', 'not json'])
    def test_invalid_json_in_delete(self):
        """Test error when DELETE data is not valid JSON"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'httpbin.org', '-PATCH', '-d', '{"key": invalid}'])
    def test_invalid_json_in_patch(self):
        """Test error when PATCH data is not valid JSON"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'httpbin.org', '-POST', '-d', ''])
    def test_empty_json_in_post(self):
        """Test error when POST data is empty string"""
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== EDGE CASES =====

    @patch('pyload.Loadtester.testurl')
    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.stats')
    @patch('pyload.sqlite3.connect')
    @patch('sys.argv', ['script.py', 'not-a-valid-url', '-GET'])
    def test_invalid_url_format(self, mock_sqlite, mock_stats, mock_insertpayload, mock_testurl):
        """Test behavior with invalid URL format"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_sqlite.return_value = mock_conn

        result = self.tester.read()
        mock_testurl.assert_called_once()

    # ===== RUNTIME ERROR HANDLING =====

    @patch('sys.argv', ['script.py', '-history'])
    @patch.object(Loadtester, 'history')
    def test_runtime_error_in_history(self, mock_history):
        """Test that RuntimeError from history() is caught"""
        mock_history.side_effect = RuntimeError("Test error")
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== VALID CASES (to ensure they don't error) =====

    @patch('pyload.Loadtester.testurl')
    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.stats')
    @patch('pyload.sqlite3.connect')
    @patch('sys.argv', ['script.py', 'httpbin.org', '-GET'])
    def test_valid_url_mode(self, mock_sqlite, mock_stats, mock_insertpayload, mock_testurl):
        """Test that valid URL mode arguments work"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_sqlite.return_value = mock_conn

        result = self.tester.read()
        mock_testurl.assert_called_once()

    @patch('sys.argv', ['script.py', '-history'])
    @patch.object(Loadtester, 'history')
    def test_valid_history_mode(self, mock_history):
        """Test that valid history mode works"""
        mock_history.return_value = None
        result = self.tester.read()
        mock_history.assert_called_once()


# Test cases for stats function
class TestLoadTesterCalculateStats(unittest.TestCase):
    def setUp(self):
        self.loadtester = Loadtester()

    def test_stats_basic(self):
        # Test normal calculation with multiple values
        totreqtime = [1.0, 2.0, 3.0]
        firstbytetime = [0.1, 0.2, 0.3]
        lastbytetime = [0.5, 1.0, 1.5]

        with patch('builtins.print') as mock_print:
            self.loadtester.stats(totreqtime, firstbytetime, lastbytetime)

            # Check that stats are printed - verify calls happened
            self.assertTrue(len(mock_print.call_args_list) > 5, "Should have multiple print calls for stats")

    def test_stats_empty_lists(self):
        # Test handling of empty lists
        totreqtime = []
        firstbytetime = []
        lastbytetime = []

        with patch('builtins.print') as mock_print:
            self.loadtester.stats(totreqtime, firstbytetime, lastbytetime)

            # Should print the error message for all empty lists
            mock_print.assert_any_call("Error!!! No requests found")

    def test_stats_empty_firstbytelist(self):
        # Test handling of empty firstbytetime list
        totreqtime = [8, 7, 6]
        firstbytetime = []
        lastbytetime = [0.2, 0.6, 0.4]

        with patch('builtins.print') as mock_print:
            self.loadtester.stats(totreqtime, firstbytetime, lastbytetime)

            # Should print the error message for empty first bytes
            mock_print.assert_any_call("Error!!! No first bytes found")

    def test_stats_empty_lastbytelist(self):
        # Test handling of empty lastbytetime list
        totreqtime = [8, 7, 6]
        firstbytetime = [0.2, 0.6, 0.4]
        lastbytetime = []

        with patch('builtins.print') as mock_print:
            self.loadtester.stats(totreqtime, firstbytetime, lastbytetime)

            # Should print the error message for empty last bytes
            mock_print.assert_any_call("Error!!! No last bytes found")

    def test_stats_single_value(self):
        # Test calculation with single-value lists
        totreqtime = [1.0]
        firstbytetime = [0.1]
        lastbytetime = [0.5]

        with patch('builtins.print') as mock_print:
            self.loadtester.stats(totreqtime, firstbytetime, lastbytetime)

            # Check that stats are printed - verify calls happened
            self.assertTrue(len(mock_print.call_args_list) > 5, "Should have multiple print calls for stats")


if __name__ == '__main__':
    unittest.main()
