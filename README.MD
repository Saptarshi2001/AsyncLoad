# AsyncLoad - Asynchronous HTTP Load Testing Tool

A high-performance, asynchronous load testing tool for HTTP endpoints built with Python and aiohttp. PyLoad can simulate concurrent requests to test the performance and reliability of web services, with integrated monitoring through Betterstack for comprehensive failure tracking.

## Features

- 🚀 **Asynchronous Testing**: High-performance async HTTP requests using aiohttp
- 📊 **Comprehensive Statistics**: Response time metrics (min, max, average) for total, first-byte, and last-byte times
- 🗄️ **Database Storage**: SQLite-based storage of all test results with history tracking
- 📈 **Betterstack Integration**: Automatic failure logging to Betterstack for monitoring
- 🔄 **Concurrent Requests**: Configurable concurrency levels for realistic load testing
- 🌐 **Multiple HTTP Methods**: Support for GET, POST, PUT, DELETE, and PATCH requests
- 📋 **Request History**: View past test results with filtering by time periods (weekly, monthly, yearly)
- ⚙️ **Flexible Configuration**: Environment-based configuration for database and monitoring
- 🧪 **Comprehensive Testing**: Full test suite with unit and integration tests

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd pyload

# Install the package
pip install -e .

# Or install dependencies manually
pip install aiohttp requests python-dotenv
```

### Install via pip

```bash
pip install async-load-tester
```

### Quick Setup

After installation, create your configuration file:

```bash
# Option 1: Create config.env (recommended)
touch config.env

# Option 2: Or create .env (development)
touch .env

# Option 3: Or set custom path
export PYLOAD_CONFIG=/path/to/your/config.env

# Then edit your chosen config file with the required settings (see Configuration section below)
```

## Configuration

**Important**: You must create a configuration file before running PyLoad. PyLoad supports flexible configuration file locations for different deployment scenarios.

### Configuration File Locations

PyLoad loads configuration in the following order (first found wins):

1. **Custom path** via `PYLOAD_CONFIG` environment variable:
   ```bash
   export PYLOAD_CONFIG=/path/to/my/custom/config.env
   pyload -u https://httpbin.org -n 10 -c 1 -GET
   ```

2. **Default config.env** in current working directory

3. **Fallback .env** in current working directory

### Creating the Configuration File

1. Create a new file named `config.env` (or `.env`) in your project directory
2. Copy the following template and update the values:

```env
# Database configuration (required)
DATABASE_URL=load.db

# Betterstack monitoring configuration (required for failure logging)
LOGTAIL_URL=https://logs.betterstack.com
LOGTAIL_TOKEN=your_betterstack_logtail_token

# Optional: Authentication credentials (only needed if testing authenticated endpoints)
USERNAME=your_username
PASSWORD=your_password

# Request timeout in seconds (required, 0 = no timeout)
timeout=30
```

### Required vs Optional Settings

- **Required**: `DATABASE_URL`, `LOGTAIL_URL`, `LOGTAIL_TOKEN`, `timeout`
- **Optional**: `USERNAME`, `PASSWORD` (only if your test endpoints require authentication)

### Getting Betterstack Credentials

1. Sign up for a Betterstack account at https://betterstack.com
2. Create a new logtail source
3. Copy the `LOGTAIL_TOKEN` from your Betterstack dashboard
4. The `LOGTAIL_URL` is typically `https://logs.betterstack.com` (already set in the template)

### Advanced Configuration

#### Using a Custom Config File Path

For production deployments or CI/CD pipelines, you can specify a custom config file:

```bash
# Set environment variable
export PYLOAD_CONFIG=/etc/pyload/production.env




#### Using .env as Fallback

If you prefer using `.env` (common in development), PyLoad will automatically load it if `config.env` is not found:

```bash
# Create .env instead of config.env
echo "DATABASE_URL=test.db" > .env
echo "LOGTAIL_TOKEN=your_token" >> .env
echo "timeout=30" >> .env
```

**Note**: PyLoad will not function properly without configuration settings. Make sure to create at least one configuration file before running any load tests.

## Usage

### Command Line Interface

PyLoad provides a comprehensive CLI for load testing:

```bash
ccload [OPTIONS] COMMAND
```

### Basic Load Testing

Test a GET endpoint with 100 requests and 10 concurrent connections:

```bash
ccload -u https://httpbin.org/get -n 100 -c 10 -GET
```

### HTTP Methods

#### GET Request
```bash
ccload -u https://jsonplaceholder.typicode.com/posts -n 50 -c 5 -GET
```

#### POST Request with JSON Data
```bash
ccload -u https://jsonplaceholder.typicode.com/posts -n 20 -c 2 -POST -d '{"title": "Test Post", "body": "This is a test", "userId": 1}'
```

#### PUT Request
```bash
ccload -u https://jsonplaceholder.typicode.com/posts/1 -n 10 -c 1 -PUT -d '{"title": "Updated Post", "body": "Updated content", "userId": 1}'
```

#### DELETE Request
```bash
ccload -u https://jsonplaceholder.typicode.com/posts/1 -n 5 -c 1 -DELETE
```

#### PATCH Request
```bash
ccload -u https://jsonplaceholder.typicode.com/posts/1 -n 5 -c 1 -PATCH -d '{"title": "Patched Title"}'
```

### History Mode

View past test results:

```bash
# View all test history
ccload -history

# View weekly summary
ccload -history -weekly

# View monthly summary
ccload -history -monthly

# View yearly summary
ccload -history -yearly
```

### Command Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `ccload` | Positional argument (can be any string) | Yes |
| `-u URL` | Target URL to test | Yes* |
| `-history` | View test history | Yes* |
| `-n NUMBER` | Number of requests to send | Yes** |
| `-c CONCURRENT` | Number of concurrent requests | Yes** |
| `-GET/-POST/-PUT/-DELETE/-PATCH` | HTTP method to use | Yes** |
| `-d DATA` | JSON data for POST/PUT/PATCH/DELETE | No |
| `-weekly/-monthly/-yearly` | Time period for history | No |

*Either `-u` or `-history` must be specified
**Required when using `-u` mode

### Examples

#### Load Testing API Endpoints

```bash
# Test posts endpoint
ccload -u https://jsonplaceholder.typicode.com/posts -n 1000 -c 50 -GET

# Test user creation endpoint
ccload -u https://reqres.in/api/users -n 100 -c 10 -POST -d '{"name": "John Doe", "job": "developer"}'

# Test data endpoint
ccload -u https://httpbin.org/json -n 500 -c 25 -GET
```

#### Performance Testing

```bash
# High concurrency test
ccload -u https://httpbin.org/delay/1 -n 1000 -c 100 -GET

# Stress test with timeout
ccload -u https://httpbin.org/delay/2 -n 100 -c 10 -GET
```

#### Monitoring Integration

```bash
# Test with Betterstack monitoring
ccload -u https://httpbin.org/status/500 -n 100 -c 5 -GET
# Check Betterstack dashboard for any failures
```

## Output

### Test Results

```
Running....
                    Load Test Results
Total Requests:                    100
Concurrent Requests:                10
Successful Requests:                98
Failed Requests:                      2
------------------------------------------------------------
Error occured!!! Please look into betterstack for more details

Performance Statistics
------------------------------------------------------------
Total Response Time (seconds):
  Maximum:                      2.345000
  Minimum:                      0.123000
  Average:                      0.567000

First Byte Time (seconds):
  Maximum:                      0.234000
  Minimum:                      0.045000
  Average:                      0.089000

Last Byte Time (seconds):
  Maximum:                      2.123000
  Minimum:                      0.078000
  Average:                      0.456000

Individual Request Details
------------------------------------------------------------
Request ID | Timestamp          | URL                        | Status | Method | Response Time
1          | 1704067200.123     | https://httpbin.org/get    | 200    | GET    | 0.567000
2          | 1704067201.456     | https://httpbin.org/get    | 200    | GET    | 0.523000
...
```

### History Output

```
Request id    |    timestamp   |     url    |      status    |        reqtype        |week
1             | 2023-01-01 12:00:00 | https://httpbin.org/get | 200 | GET | 1
2             | 2023-01-01 12:00:01 | https://httpbin.org/get | 200 | GET | 1
...
```

## Architecture

### Core Components

#### Loadtester Class
- Main class handling all load testing functionality
- Manages argument parsing, request execution, and result storage

#### Key Methods
- `read()`: Command-line argument parsing and validation
- `testurl()`: Core async load testing logic
- `insertpayload()`: Database storage of test results
- `calculatestats()`: Statistical analysis of response times
- `history()`: Historical test result retrieval
- `desc()`: Formatted output of test results

### Database Schema

```sql
CREATE TABLE LOADTEST(
    REQUESTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    TIMESTAMP TEXT NOT NULL,
    URL TEXT NOT NULL,
    STATUS INTEGER NOT NULL,
    REQTYPE VARCHAR NOT NULL,
    RESPONSETIME TEXT NOT NULL
)
```

### Monitoring Integration

Failed requests are automatically logged to Betterstack using the logtail handler. The logs include detailed failure information and can be forwarded to Loki/Grafana for visualization. Each failure log contains:

- Timestamp (nanoseconds)
- Target URL
- HTTP status code
- Request method
- Full response body for debugging

Example log structure sent to Betterstack:

```json
{
  "timestamp": "1704067200123456789",
  "url": "https://httpbin.org/status/500",
  "status": 500,
  "method": "GET",
  "body": "{\"error\": \"Internal Server Error\"}"
}
```

## Testing

### Running Tests

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

### Test Coverage

- **testload.py**: Argument parsing, validation, and statistics calculation
- **testasync.py**: Async HTTP request testing with mocking
- **testdb.py**: Database operations and connection handling

### Test Structure

```
tests/
├── __init__.py
├── testload.py      # CLI and core logic tests
├── testasync.py     # Async functionality tests
└── testdb.py        # Database operation tests
```

## Development



### Adding New Features

1. **New HTTP Methods**: Add support in argument parser and request logic
2. **Additional Metrics**: Extend statistics calculation in `calculatestats()`
3. **New Output Formats**: Modify `desc()` method for custom formatting
4. **Monitoring Integration**: Update Betterstack log structure in `testurl()`

### Code Style

- Follow PEP 8 Python style guidelines
- Use async/await for all I/O operations
- Comprehensive error handling and logging
- Unit tests for all new functionality

## Troubleshooting

### Common Issues

#### Database Connection Errors
```
Error: no such table: LOADTEST
```
**Solution**: The database table will be created automatically on first run. Ensure write permissions in the working directory.

#### Betterstack Connection Errors
```
ConnectionError: Failed to connect to Betterstack
```
**Solution**: Verify LOGTAIL_URL and LOGTAIL_TOKEN in `config.env` and ensure your Betterstack account is active.

#### High Memory Usage
**Solution**: Reduce concurrency (`-c`) parameter or increase system memory. PyLoad is memory-efficient but high concurrency requires adequate resources.

#### Timeout Errors
```
asyncio.TimeoutError: Timeout occurred
```
**Solution**: Increase timeout value in `config.env` or reduce concurrency.

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python -m unittest`)
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
python -m unittest

# Run with coverage
coverage run -m unittest
coverage report
```

## License

MIT License - see LICENSE file for details.

## Support

For issues, questions, or contributions:

- Create an issue on GitHub
- Check existing documentation and tests
- Review error logs and configuration

## Changelog

### Version 0.1.1
- Initial release
- Basic async load testing functionality
- SQLite database storage
- Betterstack monitoring integration
- Comprehensive test suite
- CLI interface with multiple HTTP methods
- Statistics calculation and reporting
- History mode for past results
