import argparse
import json
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from .checker import check_url
from .output import print_result


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simple website availability monitor"
    )

    parser.add_argument("urls", nargs="*")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--slow", type=float, default=None)
    parser.add_argument("--follow-redirects", action="store_true")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--file",
        help="Read URLs from file (one per line)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only result labels",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failure",
    )
    parser.add_argument(
        "--output",
        help="Write results to JSON file",
    )
    parser.add_argument(
        "--user-agent",
        help="Custom User-Agent header",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of concurrent workers (default: 1)",
    )

    args = parser.parse_args()

    # Reuse HTTP connections instead of opening a new one per request.
    session = requests.Session()

    if args.workers < 1:
        print("WARNING: --workers must be >= 1")
        sys.exit(2)

    workers = args.workers

    if workers > 1 and args.fail_fast:
        print("WARNING: --fail-fast ignored when using --workers > 1")

    urls = []
    user_agent = args.user_agent or DEFAULT_USER_AGENT

    if args.urls:
        urls.extend(args.urls)

    if args.file:
        with open(args.file) as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                urls.append(line)

    if not urls:
        print("No URLs provided")
        sys.exit(2)

    timeout = args.timeout
    retries = args.retries
    slow_threshold = args.slow
    follow_redirects = args.follow_redirects
    json_output = args.json

    all_results = []

    if workers == 1:
        for url in urls:
            result = check_url(
                session,
                url,
                timeout,
                retries,
                slow_threshold,
                follow_redirects,
                json_output,
                args.quiet,
                user_agent,
            )

            all_results.append(result)

            if not json_output:
                print_result(result, quiet=args.quiet)

            if args.fail_fast and result["label"] not in ("OK", "REDIRECT"):
                break

    else:
        # Threading helps for I/O-bound HTTP requests.
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    check_url,
                    session,
                    url,
                    timeout,
                    retries,
                    slow_threshold,
                    follow_redirects,
                    json_output,
                    args.quiet,
                    user_agent,
                ): url
                for url in urls
            }

            for future in as_completed(futures):
                result = future.result()
                all_results.append(result)

                if not json_output:
                    print_result(result, quiet=args.quiet)

    has_failure = any(
        result["label"] not in ("OK", "REDIRECT")
        for result in all_results
    )

    if json_output:
        print(json.dumps(all_results, indent=2))

    elif not args.quiet:
        print("\nSummary:")

        counts = Counter(result["label"] for result in all_results)

        print(f"OK: {counts['OK']}")
        print(f"REDIRECT: {counts['REDIRECT']}")
        print(f"CLIENT_ERROR: {counts['CLIENT_ERROR']}")
        print(f"SERVER_ERROR: {counts['SERVER_ERROR']}")

        errors = (
            counts["TIMEOUT"]
            + counts["DNS_ERROR"]
            + counts["SSL_ERROR"]
            + counts["CONNECTION_ERROR"]
            + counts["ERROR"]
        )

        print(f"ERRORS: {errors}")
        print(f"TOTAL: {len(all_results)}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)

    if has_failure:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()