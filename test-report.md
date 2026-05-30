# AsyncLoad Test Report

## Summary

Result:

```text
19 passed
```

Commands run:

```powershell
pytest -ra
python -m compileall src tests
pytest --collect-only
```

The MongoDB integration test ran successfully. It was not skipped.

The large Textual history-render smoke test generated:

```text
C:\Users\SAPTAR~1\AppData\Local\Temp\asyncload-large-history-test.svg
```

## New Coverage Added

These previously missing areas are now covered:

- Full real HTTP load-test integration against a local aiohttp test server.
- Exact p95/p99 calculation behavior with controlled latency samples.
- Failure accounting for mixed successful and failed HTTP responses.

## Test Files

### `tests/test_async.py`

1. `TestLoadRunner::test_run_handles_runtime_errors`
   - Unit test.
   - Verifies `LoadRunner.run()` handles a runtime error from `aiohttp.ClientSession`.
   - Confirms the terminal is not launched after the failure.

2. `TestLoadRunner::test_runner_can_be_created`
   - Unit test.
   - Verifies `LoadRunner` can be instantiated.

### `tests/test_db.py`

1. `TestEnv::test_getenv_returns_env_dataclass`
   - Unit test.
   - Verifies environment variables are converted into the `Env` dataclass.

2. `TestRecord::test_getmetrics_filters_by_timemode`
   - Unit test with mocked MongoDB.
   - Verifies `Record.getmetrics("weekly")` calls Mongo aggregation and returns records.
   - Checks the aggregation includes the final `$match` that removes URLs with no matching metrics.

3. `TestRecord::test_insertmetrics_connects_to_configured_collection`
   - Unit test with mocked MongoDB.
   - Verifies `Record.insertmetrics()` connects to the configured database and collection.
   - Verifies `update_one()` is called.
   - Verifies the Mongo client is closed.

### `tests/test_integration.py`

1. `TestMongoIntegration::test_insert_and_get_weekly_metrics_with_real_mongodb`
   - MongoDB integration test.
   - Connects to a real MongoDB instance.
   - Drops a temporary test collection.
   - Inserts one metric snapshot through `Record.insertmetrics()`.
   - Fetches weekly records through `Record.getmetrics("weekly")`.
   - Verifies the inserted URL and metric data are returned.
   - Cleans up the temporary collection afterward.

2. `TestLoadRunnerHttpIntegration::test_full_load_test_against_local_http_server`
   - Real HTTP integration test.
   - Starts a local aiohttp server.
   - Runs `LoadRunner.run()` against that server.
   - Verifies total request count, concurrency input, success count, failure count, and generated latency metrics.

3. `TestLoadRunnerHttpIntegration::test_mixed_success_and_failure_accounting_with_local_http_server`
   - Real HTTP integration test.
   - Starts a local aiohttp server that alternates `200` and `500` responses.
   - Verifies `success`, `failures`, and `error_rate`.

4. `TestLoadRunnerMetricCalculations::test_p95_and_p99_are_calculated_from_controlled_ttlb_samples`
   - Controlled metric calculation test.
   - Uses fake response timing values.
   - Verifies exact `p95`, `p99`, min/max TTLB, average latency, throughput, success count, and failure count.

5. `TestTerminalIntegration::test_large_history_render_smoke`
   - UI integration smoke test.
   - Builds a large history payload with 3 endpoints and 40 metric snapshots per endpoint.
   - Runs the Textual TUI in headless mode.
   - Saves an SVG screenshot.
   - Verifies the screenshot exists and is non-empty.

### `tests/test_load.py`

1. `TestProtocolParser::test_parse_rejects_concurrency_above_total_requests`
   - Unit test.
   - Verifies parser rejects `-c` greater than `-n`.

2. `TestProtocolParser::test_parse_rejects_multiple_http_methods`
   - Unit test.
   - Verifies parser rejects conflicting HTTP method flags.

3. `TestProtocolParser::test_parser_registers_loadrunner_cli_options`
   - Unit test.
   - Verifies expected CLI flags are registered.

4. `TestMain::test_main_runs_history_mode`
   - Unit test.
   - Verifies `main()` calls `Record.getmetrics()` and launches `Terminal` in history mode.

5. `TestMain::test_main_runs_load_test`
   - Unit test.
   - Verifies `main()` calls `LoadRunner.run()` for normal load-test mode.

6. `TestPackageExports::test_loadrunner_is_exported_from_package`
   - Unit test.
   - Verifies `LoadRunner` is exported from the package.

7. `TestTerminal::test_metric_row_formats_values`
   - Unit test.
   - Verifies `MetricRow` formats counts, latency metrics, throughput, `None`, and strings correctly.

8. `TestTerminal::test_terminal_stores_history`
   - Unit test.
   - Verifies `Terminal` stores history data and switches into history mode.

9. `TestTerminal::test_terminal_stores_metrics`
   - Unit test.
   - Verifies `Terminal` stores current metrics and keeps the command palette disabled.

## MongoDB Setup

### Option 1: Docker

Run MongoDB locally:

```powershell
docker run --name asyncload-mongo -p 27017:27017 -d mongo:latest
```

Check that it is running:

```powershell
docker ps
```

### Option 2: Existing MongoDB

If MongoDB is already installed locally, make sure it is listening on:

```text
mongodb://127.0.0.1:27017
```

You can test from Python:

```powershell
python -c "import pymongo; c=pymongo.MongoClient('mongodb://127.0.0.1:27017', serverSelectionTimeoutMS=1000); print(c.admin.command('ping')); c.close()"
```

Expected output includes:

```text
{'ok': 1.0}
```

## Configure AsyncLoad for MongoDB

Your `config.env` should use uppercase keys:

```env
MONGO_URL=mongodb://127.0.0.1:27017
MONGO_DATABASE=asyncload
MONGO_COLLECTION=metrics
TIMEOUT=10
TOTAL_REQUESTS=10
CONCURRENT_REQUESTS=2
HTTP_METHOD=get
```

## Run AsyncLoad Yourself

From the repo root:

```powershell
$env:PYTHONPATH="src"; python -m asyncload.cli https://httpbin.org/get -n 5 -c 2 -GET
```

Alternative using typicode:

```powershell
$env:PYTHONPATH="src"; python -m asyncload.cli https://jsonplaceholder.typicode.com/posts -n 5 -c 2 -GET
```

To test POST with a payload:

```powershell
$env:PYTHONPATH="src"; python -m asyncload.cli https://httpbin.org/post -n 5 -c 2 -POST -d "{\"name\":\"asyncload\"}"
```

## Check Whether Records Were Inserted

Use Python:

```powershell
python -c "import pymongo; c=pymongo.MongoClient('mongodb://127.0.0.1:27017'); docs=list(c['asyncload']['metrics'].find({}, {'_id':0})); print(docs); c.close()"
```

You should see documents shaped like:

```json
{
  "url": "https://httpbin.org/get",
  "metrics": [
    {
      "timestamp": "...",
      "p99": 123.4,
      "p95": 95.6,
      "throughput": 10.2,
      "avg_latency": 80.1,
      "max_ttfb": 20.0,
      "min_ttfb": 5.0,
      "max_ttlb": 130.0,
      "min_ttlb": 30.0,
      "successes": 5,
      "failures": 0,
      "number_of_requests": 5,
      "number_of_concurrent_requests": 2
    }
  ]
}
```

## View History in the TUI

Weekly:

```powershell
$env:PYTHONPATH="src"; python -m asyncload.cli -history -weekly
```

Monthly:

```powershell
$env:PYTHONPATH="src"; python -m asyncload.cli -history -monthly
```

Yearly:

```powershell
$env:PYTHONPATH="src"; python -m asyncload.cli -history -yearly
```
