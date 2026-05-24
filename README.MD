# AsyncLoad

AsyncLoad is an asynchronous load testing CLI designed to stress test your applications under heavy concurrent load. It contains database storage for session history as well as a Betterstack integration for monitoring and observability.

---

## Installation

### Install from pip

For version releases, use pip:

```bash
pip install AsyncLoad
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

### Basic load test

```bash
asyncload https://jsonplaceholder.typicode.com/posts -n 5 -c 2 -GET
```

```
Running....
============================================================
                     Load Test Results
============================================================
Total Requests:                    5
Concurrent Requests:               2
Successful Requests:               5
Failed Requests:                   0
------------------------------------------------------------
                 Individual Request Details
------------------------------------------------------------
Request ID   | Timestamp           | URL                            | Status   | Method    | Response Time
----------------------------------------------------------------------------------------------------------
594          | 24:05:2026 14:53:36 | https://jsonplaceholder.typico | 200      | get       | 0.337788
595          | 24:05:2026 14:53:36 | https://jsonplaceholder.typico | 200      | get       | 0.392194
596          | 24:05:2026 14:53:36 | https://jsonplaceholder.typico | 200      | get       | 0.453631
597          | 24:05:2026 14:53:36 | https://jsonplaceholder.typico | 200      | get       | 0.535650
598          | 24:05:2026 14:53:36 | https://jsonplaceholder.typico | 200      | get       | 0.573828
============================================================


                   Performance Statistics
------------------------------------------------------------
Total Response Time (seconds)
  Maximum:          0.573828
  Minimum:          0.337788
  Average:          0.458618

First Byte Time (seconds)
  Maximum:          0.573208
  Minimum:          0.337749
  Average:          0.456585

Last Byte Time (seconds)
  Maximum:          0.573827
  Minimum:          0.337787
  Average:          0.458618
============================================================
```

### Viewing history

```bash
asyncload -history
```

```
Request ID   | Timestamp           | URL                       | Status   | Method    | Response Time
-------------------------------------------------------------------------------------------------------
594          | 24:05:2026 14:53:36 | https://jsonplaceholder.t | 200      | get       | 0.337788
595          | 24:05:2026 14:53:36 | https://jsonplaceholder.t | 200      | get       | 0.392194
596          | 24:05:2026 14:53:36 | https://jsonplaceholder.t | 200      | get       | 0.453631
597          | 24:05:2026 14:53:36 | https://jsonplaceholder.t | 200      | get       | 0.535650
598          | 24:05:2026 14:53:36 | https://jsonplaceholder.t | 200      | get       | 0.573828
```

### Viewing weekly history

```bash
asyncload -history -weekly
```

```
Request ID   | Timestamp           | URL                       | Status   | Method    | Response Time    | Week
--------------------------------------------------------------------------------------------------------------
594          | 24:05:2026 14:53:36 | https://jsonplaceholder.t | 200      | get       | 0.337788         | 21
595          | 24:05:2026 14:53:36 | https://jsonplaceholder.t | 200      | get       | 0.392194         | 21
596          | 24:05:2026 14:53:36 | https://jsonplaceholder.t | 200      | get       | 0.453631         | 21
597          | 24:05:2026 14:53:36 | https://jsonplaceholder.t | 200      | get       | 0.535650         | 21
598          | 24:05:2026 14:53:36 | https://jsonplaceholder.t | 200      | get       | 0.573828         | 21
```

### POST request with payload

```bash
asyncload https://jsonplaceholder.typicode.com/posts -n 5 -c 2 -POST -d '{"title": "foo", "body": "bar", "userId": 1}'
```

```
Running....
============================================================
                     Load Test Results
============================================================
Total Requests:                    5
Concurrent Requests:               2
Successful Requests:               5
Failed Requests:                   0
------------------------------------------------------------
                 Individual Request Details
------------------------------------------------------------
Request ID   | Timestamp           | URL                            | Status   | Method    | Response Time
----------------------------------------------------------------------------------------------------------
599          | 24:05:2026 14:56:05 | https://jsonplaceholder.typico | 201      | post      | 0.592419
600          | 24:05:2026 14:56:05 | https://jsonplaceholder.typico | 201      | post      | 1.002274
601          | 24:05:2026 14:56:05 | https://jsonplaceholder.typico | 201      | post      | 1.025395
602          | 24:05:2026 14:56:05 | https://jsonplaceholder.typico | 201      | post      | 1.347690
603          | 24:05:2026 14:56:05 | https://jsonplaceholder.typico | 201      | post      | 1.392546
============================================================


                   Performance Statistics
------------------------------------------------------------
Total Response Time (seconds)
  Maximum:          1.392546
  Minimum:          0.592419
  Average:          1.072065

First Byte Time (seconds)
  Maximum:          1.392511
  Minimum:          0.592399
  Average:          1.072046

Last Byte Time (seconds)
  Maximum:          1.392546
  Minimum:          0.592419
  Average:          1.072064
============================================================
```

### High concurrency test

```bash
asyncload https://jsonplaceholder.typicode.com/posts -n 20 -c 10 -GET
```

```
Running....
============================================================
                     Load Test Results
============================================================
Total Requests:                   20
Concurrent Requests:              10
Successful Requests:              20
Failed Requests:                   0
------------------------------------------------------------
                 Individual Request Details
------------------------------------------------------------
Request ID   | Timestamp           | URL                            | Status   | Method    | Response Time
----------------------------------------------------------------------------------------------------------
609          | 24:05:2026 14:57:12 | https://jsonplaceholder.typico | 200      | get       | 0.395732
610          | 24:05:2026 14:57:12 | https://jsonplaceholder.typico | 200      | get       | 0.397407
...
628          | 24:05:2026 14:57:12 | https://jsonplaceholder.typico | 200      | get       | 1.824638
============================================================


                   Performance Statistics
------------------------------------------------------------
Total Response Time (seconds)
  Maximum:          1.824638
  Minimum:          0.395732
  Average:          0.861470

First Byte Time (seconds)
  Maximum:          1.824627
  Minimum:          0.383778
  Average:          0.857246

Last Byte Time (seconds)
  Maximum:          1.824638
  Minimum:          0.395731
  Average:          0.861470
============================================================
```

---

## API Reference

## GlobalConfig

### platform_path

sets up the global config variable accordingly with the underlying os 

- "%LOCALAPPDATA%/asyncload/config.env" for Windows
- "~/.config/asyncload/config.env" for Linux/Mac

### ensure_global_config()

Creates the global config file in the user's system


## Loadtester

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
| `reqlist` | `list` | http request results to be stored |

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
