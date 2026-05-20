def load_urls(args) -> list[str]:
    urls = []

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

    return urls