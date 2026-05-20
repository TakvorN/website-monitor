import argparse


def build_parser() -> argparse.ArgumentParser:
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

    return parser