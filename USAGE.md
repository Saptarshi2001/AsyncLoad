# Usage Guide

## Quick Start

### Clone repo (local config)

```bash
pip install -r requirements.txt
cp config.env.example config.env
# Edit config.env with your MongoDB settings, TIMEOUT, TOTAL_REQUESTS, CONCURRENT_REQUESTS, HTTP_METHOD
python asyncload https://example.com
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
MONGO_URL=mongodb://127.0.0.1:27017
MONGO_DATABASE=asyncload
MONGO_COLLECTION=metrics
TIMEOUT=10
TOTAL_REQUESTS=100
CONCURRENT_REQUESTS=10
HTTP_METHOD=get
```

Then run from anywhere:
```bash
asyncload https://example.com
```

### Using Docker

```bash
docker compose build
docker compose run --rm asyncload https://example.com
```

Docker Compose starts MongoDB for you and overrides the app container's `MONGO_URL` to `mongodb://mongo:27017`. Your local `config.env` can still use `mongodb://127.0.0.1:27017` for non-Docker runs.

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
asyncload https://example.com          # Uses n=200, c=20, method=post from config
```

### Option B: CLI flags (quick one-off override)

```bash
asyncload https://example.com -n 500 -c 50    # Override n and c for this run
asyncload https://example.com -POST           # Override method for this run
asyncload https://example.com -n 500 -c 50 -POST  # Override all three
```

### Priority order

```
CLI flag (-n 500) → config file → hardcoded default (100 / 10 / get)
```

---

## Examples

```bash
# Minimal — uses config defaults
asyncload https://jsonplaceholder.typicode.com/posts

# Override method
asyncload https://jsonplaceholder.typicode.com/posts -POST

# Override n and c
asyncload https://httpbin.org/delay/1 -n 1000 -c 100

# With JSON data
asyncload https://reqres.in/api/users -POST -d '{"name": "John"}'

# View history
asyncload -history
asyncload -history -weekly
asyncload -history -monthly
asyncload -history -yearly
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
asyncload [url] [-history] [-n N] [-c C] [-GET | -POST | -PUT | -DELETE | -PATCH]
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
docker compose run --rm asyncload https://example.com

# Run with CLI overrides
docker compose run --rm asyncload https://example.com -n 500 -c 50 -POST
```



try:
            dburl = os.getenv("DATABASE_URL") or "load.db"
            conn=sqlite3.connect(dburl)
            curr=conn.cursor()
            data=curr.execute("SELECT * FROM Session_History").fetchall()
            conn.commit()
            conn.close()


def desc(self,reqlist):
        print(f"{'Individual Request Details':^60}")
        print(f"{'-'*60}")

        # Print table header
        header = f"{'Request ID':<12} | {'Timestamp':<19} | {'URL':<30} | {'Status':<8} | {'Method':<9} | {'Response Time'}"
        print(header)
        print("-" * len(header))

        # Print each request
        for lst in reqlist:
            reqid = lst[0]
            try:
                dt = datetime.datetime.strptime(lst[1], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.datetime.fromtimestamp(float(lst[1]))
            timestamp = dt.strftime("%d:%m:%Y %H:%M:%S")
            url = str(lst[2])[:30]        # Truncate URL if too long
            status = lst[3]
            reqtype = str(lst[4])
            responsetime = f"{lst[5]:.6f}"  # Format response time to 6 decimal places

            print(f"{reqid:<12} | {timestamp:<19} | {url:<30} | {status:<8} | {reqtype:<9} | {responsetime}")

        print(f"{'='*60}")
