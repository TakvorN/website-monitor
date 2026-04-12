import sys
import requests
import time
import argparse

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def check_url(url: str, timeout: float, retries: int, slow_threshold: float, follow_redirects) -> None:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    for attempt in range(1, retries + 1):
        print(f"Checking {url} ({attempt}/{retries})...")
        start = time.perf_counter()

        try:
            response = requests.get(url, timeout=timeout, allow_redirects=follow_redirects)
            status_code = response.status_code
            
        except requests.exceptions.Timeout:
            label = "TIMEOUT"

        except requests.exceptions.SSLError:
            label = "SSL_ERROR"

        except requests.exceptions.ConnectionError as e:

            if "NameResolutionError" in str(e):
                label = "DNS_ERROR"
            else:
                label = "CONNECTION_ERROR"

        except requests.exceptions.RequestException:
            label = "ERROR"

        else:    
            end = time.perf_counter()
            duration_ms = (end - start) * 1000
            is_slow = slow_threshold is not None and duration_ms > slow_threshold

            if 200 <= status_code < 300:
                color = GREEN
                label = "OK"
            elif 300 <= status_code < 400:
                color = YELLOW
                label = "REDIRECT"
            elif 400 <= status_code < 500:
                color = RED
                label = "CLIENT_ERROR"
            else:
                color = RED
                label = "SERVER_ERROR"

            if is_slow:
                color = YELLOW
                label = "SLOW"

            print(f"{url} -> {color}{label} {status_code}{RESET} ({duration_ms:.2f} ms)")
            return label
        
          
        if attempt == retries:
            end = time.perf_counter()
            duration_ms = (end - start) * 1000

            print(f"{url} -> {RED}{label}{RESET} ({duration_ms:.2f} ms)")
            return label

        else:
            time.sleep(0.5)



def main():

    parser = argparse.ArgumentParser(
        description="Simple website availability monitor"
)
    
    parser.add_argument("urls", nargs="+")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--slow", type=float, default=None)
    parser.add_argument("--follow-redirects", action="store_true")
    
    args = parser.parse_args()

    urls = args.urls
    timeout = args.timeout
    retries = args.retries
    slow_threshold = args.slow
    follow_redirects = args.follow_redirects

    results = []

    for url in urls:
        result = check_url(url, timeout, retries, slow_threshold, follow_redirects)
        results.append(result)

    print("\nSummary:")

    from collections import Counter
    counts = Counter(results)

    print(f"OK: {counts['OK']}")
    print(f"REDIRECT: {counts['REDIRECT']}")
    print(f"CLIENT_ERROR: {counts['CLIENT_ERROR']}")
    print(f"SERVER_ERROR: {counts['SERVER_ERROR']}")

    errors = (
        counts['TIMEOUT']
        + counts['DNS_ERROR']
        + counts['SSL_ERROR']
        + counts['CONNECTION_ERROR']
        + counts['ERROR']
    )

    print(f"ERRORS: {errors}")
    print(f"TOTAL: {len(results)}")


if __name__ == "__main__":
    main()