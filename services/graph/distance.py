import re


def meters(s: str) -> float:
    match = re.match(r"^(\d+)m", s)

    if match := re.match(r"^(\d+)mi", s):
        # miles to meters
        return int(match[1]) * 1609.34
    elif match := re.match(r"^(\d+)km", s):
        # km to meters
        return int(match[1]) * 1000
    elif match := re.match(r"^(\d+)m", s):
        # meters
        return int(match[1])
    else:
        raise ValueError("invalid distance")
