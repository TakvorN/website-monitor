# Website Monitor CLI

Simple Python command-line tool for monitoring website availability and response time.

## Features

- Check one or multiple URLs
- Retry failed requests
- Detect slow responses
- Follow redirects optionally
- Read URLs from file input
- Output results as JSON
- Save JSON results to file
- Quiet mode for scripting
- Fail-fast mode
- Custom User-Agent support
- Concurrent checks with multiple workers

## Installation

Clone the repository:

```bash
git clone https://github.com/TakvorN/website-monitor.git
cd website-monitor
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -e .
```

## Usage

Check a single website:

```bash
website-monitor example.com
```

Check multiple websites:

```bash
website-monitor example.com google.com
```

Read URLs from a file:

```bash
website-monitor --file sample_urls.txt
```

Output JSON:

```bash
website-monitor example.com --json
```

Run checks concurrently:

```bash
website-monitor example.com google.com github.com --workers 3
```

## Example Output

```text
Checking https://example.com (1/1)...
https://example.com -> OK 200 (123.45 ms)

Summary:
OK: 1
REDIRECT: 0
CLIENT_ERROR: 0
SERVER_ERROR: 0
ERRORS: 0
TOTAL: 1
```

## Running Tests

Run the test suite with:

```bash
pytest
```

## Future Enhancements

Possible next steps for this project:

- SSL certificate expiration checks
- Scheduled monitoring with cron/systemd
- Email or Slack alert notifications
- Browser-based checks with Selenium
- Metrics export for Prometheus/Grafana
