import sys
import requests
import time

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
    if len(sys.argv) < 2:
        print("Usage: python main.py <url>")
        sys.exit(1)

    timeout = 10
    retries = 1
    slow_threshold = None
    follow_redirects = False
    args = sys.argv[1:]

    if "--timeout" in args:
        index = args.index("--timeout")

        if index + 1 >= len(args):
            print("Error: --timeout requires value")
            sys.exit(1)

        timeout = float(args[index + 1])
        del args[index:index+2]

    if "--retries" in args:
        index = args.index("--retries")

        try:
            retries = int(args[index + 1])

            if retries < 1:
                print("Error: --retries must be >= 1")
                sys.exit(1)

        except (IndexError, ValueError):
            print("Error: --retries requires an integer")
            sys.exit(1)

        del args[index:index + 2]


    if "--slow" in args:
        index = args.index("--slow")

        try:
            slow_threshold = float(args[index + 1])
        except (IndexError, ValueError):
            print("Error: --slow requires milliseconds value")
            sys.exit(1)

        if slow_threshold < 0:
            print("Error: --slow must be >= 0")
            sys.exit(1)

        del args[index:index + 2]



    if "--follow-redirects" in args:
        follow_redirects = True
        args.remove("--follow-redirects")

    urls = args

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