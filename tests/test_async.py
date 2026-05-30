import asyncio
import unittest
from unittest.mock import MagicMock, patch

from asyncload import LoadRunner


class TestLoadRunner(unittest.TestCase):
    def test_runner_can_be_created(self):
        runner = LoadRunner()

        self.assertIsInstance(runner, LoadRunner)

    def test_view_session_history_is_currently_a_noop(self):
        runner = LoadRunner()

        self.assertIsNone(runner.view_session_history())
        self.assertIsNone(runner.view_session_history(timemode="weekly"))

    @patch("asyncload.cli.Terminal")
    @patch("asyncload.cli.aiohttp.ClientSession")
    @patch("asyncload.cli.aiohttp.TCPConnector")
    @patch("asyncload.cli.getenv")
    def test_run_handles_runtime_errors(
        self, mock_getenv, mock_connector, mock_session, mock_terminal
    ):
        runner = LoadRunner()
        mock_getenv.return_value = MagicMock(TIMEOUT=1)
        mock_session.side_effect = RuntimeError("boom")

        async def run_case():
            return await runner.run(
                "https://example.com",
                numreq=1,
                conreq=1,
                reqtype="get",
            )

        import asyncio

        result = asyncio.run(run_case())

        self.assertIsNone(result)
        mock_connector.assert_called_once_with(limit=1, limit_per_host=1)
        mock_terminal.assert_not_called()


if __name__ == "__main__":
    unittest.main()
