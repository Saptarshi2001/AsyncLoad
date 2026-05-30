import argparse
import unittest
from unittest.mock import MagicMock, patch

from asyncload import LoadRunner, main
from asyncload.parser import Params, ProtocolParser
from asyncload.terminal import MetricRow, Terminal


class TestProtocolParser(unittest.TestCase):
    def test_parser_registers_loadrunner_cli_options(self):
        option_strings = {
            option
            for action in ProtocolParser().parser._actions
            for option in action.option_strings
        }

        self.assertIn("-history", option_strings)
        self.assertIn("-setup", option_strings)
        self.assertIn("-n", option_strings)
        self.assertIn("-c", option_strings)
        self.assertIn("-GET", option_strings)
        self.assertIn("-POST", option_strings)

    @patch("sys.argv", ["asyncload", "https://example.com", "-n", "2", "-c", "3"])
    def test_parse_rejects_concurrency_above_total_requests(self):
        with self.assertRaises(SystemExit):
            ProtocolParser().parse()

    @patch("sys.argv", ["asyncload", "https://example.com", "-GET", "-POST"])
    def test_parse_rejects_multiple_http_methods(self):
        with self.assertRaises(argparse.ArgumentError):
            ProtocolParser().parse()


class TestMain(unittest.TestCase):
    @patch("asyncload.cli.asyncio.run")
    @patch("asyncload.cli.LoadRunner")
    @patch("asyncload.cli.ProtocolParser")
    def test_main_runs_load_test(self, mock_parser_class, mock_runner_class, mock_run):
        mock_parser_class.return_value.parse.return_value = Params(
            "https://example.com", 3, 1, "get", None, None
        )
        runner = MagicMock()
        mock_runner_class.return_value = runner

        main()

        runner.run.assert_called_once_with(
            "https://example.com", 3, 1, "get", None
        )
        mock_run.assert_called_once()

    @patch("asyncload.cli.LoadRunner")
    @patch("asyncload.cli.ProtocolParser")
    def test_main_runs_history_mode(self, mock_parser_class, mock_runner_class):
        mock_parser_class.return_value.parse.return_value = Params(
            None, None, None, None, "monthly", None
        )
        runner = MagicMock()
        mock_runner_class.return_value = runner

        main()

        runner.view_session_history.assert_called_once_with("monthly")


class TestTerminal(unittest.TestCase):
    def test_metric_row_formats_values(self):
        self.assertEqual(MetricRow._format_value(1200), "1,200")
        self.assertEqual(MetricRow._format_value(42.756), "42.76")
        self.assertEqual(MetricRow._format_value(None), "N/A")
        self.assertEqual(MetricRow._format_value("ok"), "ok")

    def test_terminal_stores_metrics(self):
        metrics = {"total_requests": 10}

        app = Terminal(metrics)

        self.assertIs(app.metrics, metrics)
        self.assertFalse(app.ENABLE_COMMAND_PALETTE)


class TestPackageExports(unittest.TestCase):
    def test_loadrunner_is_exported_from_package(self):
        self.assertIs(LoadRunner, LoadRunner)


if __name__ == "__main__":
    unittest.main()
