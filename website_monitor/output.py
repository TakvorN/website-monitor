GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_result(result, quiet=False) -> None:
    url = result["url"]
    label = result["label"]
    status_code = result["status_code"]
    duration_ms = result["duration_ms"]

    if quiet:
        print(result["label"])
        return

    if label == "OK":
        color = GREEN
    elif label == "REDIRECT":
        color = YELLOW
    elif label == "SLOW":
        color = YELLOW
    else:
        color = RED

    if status_code is not None:
        print(
            f"{url} -> {color}{label} "
            f"{status_code}{RESET} "
            f"({duration_ms:.2f} ms)"
        )
    else:
        print(
            f"{url} -> {color}{label}{RESET} "
            f"({duration_ms:.2f} ms)"
        )