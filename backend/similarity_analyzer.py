def find_duplicates(code: str):
    lines = code.splitlines()
    seen = {}
    duplicates = []

    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()

        # Ignore empty lines & comments
        if not line or line.startswith("#"):
            continue

        # Skip extremely small tokens
        if len(line) < 5:
            continue

        # Normalize whitespace
        key = " ".join(line.split())

        if key in seen:
            duplicates.append({
                "line_original": seen[key],
                "line_duplicate": idx + 1,
                "text": raw_line.strip()
            })
        else:
            seen[key] = idx + 1

    return duplicates
