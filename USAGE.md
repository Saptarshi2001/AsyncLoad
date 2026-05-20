# Usage Guide

## Quick Start

### Clone repo (local config)

```bash
pip install -r requirements.txt
cp config.env.example config.env
# Edit config.env with your LOGTAIL_TOKEN, LOGTAIL_URL, TOTAL_REQUESTS, CONCURRENT_REQUESTS, HTTP_METHOD
python pyload.py https://example.com
```

### Install globally with pip

```bash
pip install -e .
# or: pip install async-load-tester
```

After pip install, create a global config at:
- **Windows:** `%LOCALAPPDATA%\loadtester\config.env`
- **Linux/Mac:** `~/.config/loadtester/config.env`

Contents:
```
LOGTAIL_TOKEN=your_token
LOGTAIL_URL=your_url
TOTAL_REQUESTS=100
CONCURRENT_REQUESTS=10
HTTP_METHOD=get
```

Then run from anywhere:
```bash
pyload https://example.com
```

### Using Docker

```bash
docker compose build
docker compose run --rm server https://example.com
```

---

## Two ways to set n, c, method

### Option A: Config file (set once, use forever)

Edit your `config.env` (or global config):
```
TOTAL_REQUESTS=200
CONCURRENT_REQUESTS=20
HTTP_METHOD=post
```

Then run without any flags:
```bash
pyload https://example.com          # Uses n=200, c=20, method=post from config
```

### Option B: CLI flags (quick one-off override)

```bash
pyload https://example.com -n 500 -c 50    # Override n and c for this run
pyload https://example.com -POST           # Override method for this run
pyload https://example.com -n 500 -c 50 -POST  # Override all three
```

### Priority order

```
CLI flag (-n 500) → config file → hardcoded default (100 / 10 / get)
```

---

## Examples

```bash
# Minimal — uses config defaults
pyload https://jsonplaceholder.typicode.com/posts

# Override method
pyload https://jsonplaceholder.typicode.com/posts -POST

# Override n and c
pyload https://httpbin.org/delay/1 -n 1000 -c 100

# With JSON data
pyload https://reqres.in/api/users -POST -d '{"name": "John"}'

# View history
pyload -history
pyload -history -weekly
pyload -history -monthly
pyload -history -yearly
```

---

## Config variables

| Variable | Default | Description |
|---|---|---|
| `TOTAL_REQUESTS` | `100` | Number of total requests |
| `CONCURRENT_REQUESTS` | `10` | Number of concurrent requests |
| `HTTP_METHOD` | `get` | Default HTTP method (overridden by CLI flags) |
| `DATABASE_URL` | `load.db` | SQLite database file path |
| `timeout` | `0` | Request timeout in seconds (0 = no timeout) |
| `LOGTAIL_TOKEN` | _(required)_ | Betterstack source token |
| `LOGTAIL_URL` | _(required)_ | Betterstack endpoint URL |

Config files are read in this order (first found wins):
1. `config.env` in current directory
2. `%LOCALAPPDATA%\loadtester\config.env` (Windows) or `~/.config/loadtester/config.env` (Linux/Mac)
3. `.env` in current directory

---

## CLI Reference

```bash
pyload [url] [-history] [-n N] [-c C] [-GET | -POST | -PUT | -DELETE | -PATCH]
       [-weekly] [-monthly] [-yearly] [-d DATA]
```

| Argument | Description |
|---|---|
| `url` | URL to load test |
| `-history` | View session history |
| `-n` | Total requests (overrides config) |
| `-c` | Concurrent requests (overrides config) |
| `-GET` / `-POST` / `-PUT` / `-DELETE` / `-PATCH` | HTTP method |
| `-d` / `--data` | JSON body for POST/PUT/PATCH/DELETE |
| `-weekly` | Filter history by current week |
| `-monthly` | Filter history by current month |
| `-yearly` | Filter history by current year |

---

## Docker

```bash
# Build
docker compose build

# Run with config
docker compose run --rm server https://example.com

# Run with CLI overrides
docker compose run --rm server https://example.com -n 500 -c 50 -POST
```
