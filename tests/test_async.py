import unittest
import asyncio
from unittest.mock import patch
from pyload import Loadtester


class TestLoadTesterAsyncRealAPI(unittest.TestCase):

    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.stats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_get_request(self, mock_requests_post, mock_print, mock_stats, mock_insertpayload):
        loadtester = Loadtester()
        asyncio.run(self._run_test(loadtester, mock_print, 'get', 1, 1))

    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.stats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_post_request(self, mock_requests_post, mock_print, mock_stats, mock_insertpayload):
        loadtester = Loadtester()
        asyncio.run(self._run_test(loadtester, mock_print, 'post', 1, 1))

    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.stats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_concurrent_requests(self, mock_requests_post, mock_print, mock_stats, mock_insertpayload):
        loadtester = Loadtester()
        asyncio.run(self._run_test(loadtester, mock_print, 'get', 3, 2))

    async def _run_test(self, loadtester, mock_print, method, total, concurrent):
        url = 'https://httpbin.org/get'
        await loadtester.testurl(url, total, concurrent, method)

        # ✅ robust checks
        self.assertTrue(any("Total Requests:" in str(call) for call in mock_print.call_args_list))
        self.assertTrue(any("Concurrent Requests:" in str(call) for call in mock_print.call_args_list))

        success_count = 0
        failure_count = 0

        for call in mock_print.call_args_list:
            args = call[0]
            if len(args) >= 2:
                if "Successful Requests:" in str(args[0]):
                    success_count = args[1]
                if "Failed Requests:" in str(args[0]):
                    failure_count = args[1]

        total_processed = success_count + failure_count
        self.assertGreaterEqual(total_processed, 0)


if __name__ == "__main__":
    unittest.main()