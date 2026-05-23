# AsyncLoad

AsyncLoad is an asynchronous load testing CLI designed to stress test your applications under heavy concurrent load. It contains database storage for session history as well as a Betterstack integration for monitoring and observability.

---

## Installation

### Install from pip

For version releases, use pip:

```bash
pip install async-load-tester
asyncload -setup

Set your betterstack env variables inside the global config file thats created."%LOCALAPPDATA%/loadtester/config.env" for Windows,"~/.config/loadtester/config.env" for linux and Mac. You can setup the number of requests,concurrent requests, as well as the http method either in the config file or simply use the cmd flags to override the values. Default values for number of requests,concurrent requests,http method is 100,10,GET.   

```
Head over to your cmd and type:

```bash
asyncload https://httpbin.org/ -n 100 -c 10 -GET
```

### Install from GitHub source

For building from source, install directly from the git repository:

```bash
git clone <repository-url>
cd Asyncload
pip install .
cp config.env.example config.env # set up your config file 
python -m unittest discover tests/ # Run all tests
asyncload https://httpbin.org/ -n 100 -c 10 -GET
```

Or Use Docker to build and run the source:

```bash
docker compose build
docker compose run --rm asyncload https://httpbin.org/ -n 100 -c 10 -GET
```


### Running the tests

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test modules
python -m unittest tests.testload
python -m unittest tests.testasync
python -m unittest tests.testdb

# Run with verbose output
python -m unittest -v tests.testload
```





## Examples

```bash
# Basic GET request
asyncload https://jsonplaceholder.typicode.com/posts -n 1000 -c 50 -GET

# Test user creation endpoint
asyncload https://reqres.in/api/users -n 100 -c 10 -POST -d '{"name": "John Doe", "job": "developer"}'

# High concurrency test
asyncload https://httpbin.org/delay/1 -n 1000 -c 100 -GET

# Stress test with timeout
asyncload https://httpbin.org/delay/2 -n 100 -c 10 -GET


```

---

## API Reference

### ensure_global_config()

Creates the global config file in the user's system

### read()

Reads the command line arguments before executing the load test.

---

### testurl(url, numreq, conreq, reqtype, headers=None)

The core function of AsyncLoad. Sends requests to the specified URL asynchronously.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `url` | `str` | The URL to test |
| `numreq` | `int` | Number of total requests |
| `conreq` | `int` | Number of concurrent requests |
| `reqtype` | `str` | HTTP method (GET, POST, PUT, DELETE, etc.) |
| `headers` | `dict` | Optional HTTP headers |

---

### insertpayload(reqlist)

Stores the return values from the requests in an SQLite database instance.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `reqlist` | `list` | List of request results to store |

---

### history(timemode=None)

Retrieves the session history from the database instance.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `timemode` | `str` | Optional filter: 'weekly', 'monthly', or 'yearly' |

---

### stats(totresponsetime, firstbytetime, lastbytetime)

Calculates minimum, maximum, and average of total response time, first byte time, and last byte time.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `totresponsetime` | `list` | List of total response times |
| `firstbytetime` | `list` | List of first byte times |
| `lastbytetime` | `list` | List of last byte times |


---

### desc()

Displays the load test statistics in the terminal.



### Options

| Flag | Description |
|------|-------------|
| `-n` | Number of requests |
| `-c` | Number of concurrent requests |
| `-GET` / `-POST` / `-DELETE` / `-PUT` / `-HEAD` / `-PATCH` | HTTP method |
| `-d` | JSON data for POST/PUT/PATCH/DELETE |
| `-history` | View session history |
| `-history -weekly` | View weekly session history |
| `-history -monthly` | View monthly session history |
| `-history -yearly` | View yearly session history |

---

## Changelog

### [1.0.0] - 2026-05-11
#### Added
- Initial release of AsyncLoad
- Asynchronous load testing CLI with concurrent request support
- Database storage for session history using SQLite
- Betterstack integration for monitoring and observability
- Support for multiple HTTP methods (GET, POST, PUT, DELETE, HEAD, PATCH)
- Configurable concurrency and request count
- Session history viewing (weekly, monthly, yearly)
- Load testing stats 
