import os
import tempfile
import unittest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch

from aiohttp import web
import pymongo

from asyncload import LoadRunner
from asyncload.db import Record
from asyncload.env import EnvKeys
from asyncload.terminal import Terminal


def _mongo_url():
    return os.getenv(EnvKeys.MONGO_URL, "mongodb://127.0.0.1:27017")


def _mongo_available(url):
    try:
        client = pymongo.MongoClient(url, serverSelectionTimeoutMS=500)
        client.admin.command("ping")
        client.close()
        return True
    except Exception:
        return False


class TestMongoIntegration(unittest.TestCase):
    def test_insert_and_get_weekly_metrics_with_real_mongodb(self):
        url = _mongo_url()
        if not _mongo_available(url):
            self.skipTest("MongoDB is not reachable for integration testing")

        database = "testdb"
        collection = "testcollc"
        env = {
            EnvKeys.MONGO_URL: url,
            EnvKeys.MONGO_DATABASE: database,
            EnvKeys.MONGO_COLLECTION: collection,
        }
        client = pymongo.MongoClient(url)

        try:
            with patch.dict(os.environ, env, clear=False):
                Record().insertmetrics(
                    "https://jsonplaceholder.typicode.com/posts",
                    {
                        "p99": 140.0,
                        "p95": 95.0,
                        "throughput": 250.0,
                        "avg_latency": 55.0,
                        "maxttfb": 20.0,
                        "minttfb": 5.0,
                        "maxttlb": 140.0,
                        "minttlb": 25.0,
                        "success": 99,
                        "failures": 1,
                        "numreq": 100,
                        "conreq": 10,
                    },
                )
                records = Record().getmetrics("weekly")

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["url"], "https://jsonplaceholder.typicode.com/posts")
            self.assertEqual(len(records[0]["metrics"]), 1)
            self.assertEqual(records[0]["metrics"][0]["p95"], 95.0)
        finally:
            client[database][collection].drop()
            client.drop_database(database)
            client.close()


class TestLoadRunnerHttpIntegration(unittest.TestCase):
    async def _start_server(self, handler):
        app = web.Application()
        app.router.add_get("/load", handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]
        return runner, f"http://127.0.0.1:{port}/load"

    def test_full_load_test_against_local_http_server(self):
        async def handler(request):
            return web.Response(text="ok")

        async def run_case():
            runner, url = await self._start_server(handler)
            try:
                with (
                    patch("asyncload.cli.getenv") as mock_getenv,
                    patch("asyncload.cli.Record") as mock_record,
                    patch("asyncload.cli.Terminal") as mock_terminal,
                ):
                    mock_getenv.return_value = MagicMock(TIMEOUT=5)
                    result = await LoadRunner().run(url, numreq=5, conreq=2, reqtype="get")
                    call_args = mock_record.return_value.insertmetrics.call_args.args
                    metrics = call_args[1]
                    self.assertIs(result, metrics)
                    self.assertEqual(call_args[0], url)
                    self.assertEqual(metrics["success"], 5)
                    self.assertEqual(metrics["failures"], 0)
                    self.assertEqual(metrics["numreq"], 5)
                    self.assertEqual(metrics["conreq"], 2)
                    self.assertGreaterEqual(metrics["p95"], 0)
                    self.assertGreaterEqual(metrics["p99"], 0)
                    mock_terminal.assert_not_called()
            finally:
                await runner.cleanup()

        asyncio.run(run_case())

    def test_mixed_success_and_failure_accounting_with_local_http_server(self):
        counter = {"count": 0}

        async def handler(request):
            counter["count"] += 1
            if counter["count"] % 2 == 0:
                return web.Response(status=500, text="fail")
            return web.Response(text="ok")

        async def run_case():
            runner, url = await self._start_server(handler)
            try:
                with (
                    patch("asyncload.cli.getenv") as mock_getenv,
                    patch("asyncload.cli.Record") as mock_record,
                    patch("asyncload.cli.Terminal"),
                ):
                    mock_getenv.return_value = MagicMock(TIMEOUT=5)
                    await LoadRunner().run(url, numreq=6, conreq=3, reqtype="get")
                    metrics = mock_record.return_value.insertmetrics.call_args.args[1]
                    self.assertEqual(metrics["success"], 3)
                    self.assertEqual(metrics["failures"], 3)
                    self.assertEqual(metrics["error_rate"], 50.0)
            finally:
                await runner.cleanup()

        asyncio.run(run_case())


class _FakeContent:
    async def read(self, size=-1):
        return b"x"


class _FakeResponse:
    status = 200

    def __init__(self):
        self.content = _FakeContent()

    def close(self):
        pass


class _FakeSession:
    def __init__(self, *args, **kwargs):
        pass

    async def request(self, *args, **kwargs):
        return _FakeResponse()

    async def close(self):
        pass


class TestLoadRunnerMetricCalculations(unittest.TestCase):
    @patch("asyncload.cli.Terminal")
    @patch("asyncload.cli.Record")
    @patch("asyncload.cli.aiohttp.TCPConnector")
    @patch("asyncload.cli.aiohttp.ClientSession", _FakeSession)
    @patch("asyncload.cli.getenv")
    def test_p95_and_p99_are_calculated_from_controlled_ttlb_samples(
        self, mock_getenv, mock_connector, mock_record, mock_terminal
    ):
        mock_getenv.return_value = MagicMock(TIMEOUT=5)
        timings = iter(
            [
                0.0,
                0.0,
                0.01,
                0.10,
                0.0,
                0.02,
                0.20,
                0.0,
                0.03,
                0.30,
                1.0,
            ]
        )

        with patch("asyncload.cli.time.perf_counter", side_effect=lambda: next(timings)):
            asyncio.run(
                LoadRunner().run(
                    "https://jsonplaceholder.typicode.com/posts",
                    numreq=3,
                    conreq=3,
                    reqtype="get",
                )
            )

        metrics = mock_record.return_value.insertmetrics.call_args.args[1]
        self.assertEqual(metrics["p95"], 200.0)
        self.assertEqual(metrics["p99"], 200.0)
        self.assertEqual(metrics["maxttlb"], 300.0)
        self.assertEqual(metrics["minttlb"], 100.0)
        self.assertAlmostEqual(metrics["avg_latency"], 200.0)
        self.assertEqual(metrics["throughput"], 3.0)
        self.assertEqual(metrics["success"], 3)
        self.assertEqual(metrics["failures"], 0)


class TestTerminalIntegration(unittest.TestCase):
    def test_large_history_render_smoke(self):
        history = []
        for endpoint in range(3):
            metrics = []
            for minute in range(40):
                metrics.append(
                    {
                        "timestamp": datetime(2026, 5, 30, 10, minute % 60),
                        "p99": 140.0 + minute,
                        "p95": 95.0 + minute,
                        "throughput": 250.0,
                        "avg_latency": 55.0,
                        "max_ttfb": 20.0,
                        "min_ttfb": 5.0,
                        "max_ttlb": 140.0,
                        "min_ttlb": 25.0,
                        "successes": 99,
                        "failures": 1,
                        "number_of_requests": 100,
                        "number_of_concurrent_requests": 10,
                    }
                )
            history.append(
                {
                    "url": f"https://jsonplaceholder.typicode.com/posts/{endpoint + 1}",
                    "metrics": metrics,
                }
            )

        screenshot_name = "asyncload-large-history-test.svg"
        screenshot_path = os.path.join(tempfile.gettempdir(), screenshot_name)
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        async def capture(pilot):
            await pilot.pause(0.1)
            pilot.app.save_screenshot(screenshot_name, path=tempfile.gettempdir())
            pilot.app.exit()

        Terminal(history=history, timemode="weekly").run(
            headless=True,
            size=(120, 50),
            auto_pilot=capture,
        )

        self.assertTrue(os.path.exists(screenshot_path))
        self.assertGreater(os.path.getsize(screenshot_path), 0)


if __name__ == "__main__":
    unittest.main()
