from collections import Counter


def print_summary(results) -> None:
    print("\nSummary:")

    counts = Counter(result["label"] for result in results)

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
    print(f"TOTAL: {len(results)}")