import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from .checker import check_url
from .output import print_result
from .build_parser import build_parser
from .load_urls import load_urls
from .print_summary import print_summary



DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def main() -> None:
    args = build_parser().parse_args()

    # Reuse HTTP connections instead of opening a new one per request.
    session = requests.Session()

    if args.workers < 1:
        print("WARNING: --workers must be >= 1")
        sys.exit(2)

    workers = args.workers

    if workers > 1 and args.fail_fast:
        print("WARNING: --fail-fast ignored when using --workers > 1")

    urls = load_urls(args)

    if not urls:
        print("No URLs provided")
        sys.exit(2)
    
    user_agent = args.user_agent or DEFAULT_USER_AGENT

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
        print_summary(all_results)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)

    if has_failure:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()