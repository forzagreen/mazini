import gzip
import json
import os

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def fixture_lines(name: str) -> list[str]:
    path = os.path.join(FIXTURES, name)
    opener = gzip.open if name.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:  # type: ignore[operator]
        return [line for line in f.read().split("\n") if line]


def fixture_records(name: str) -> list[dict]:
    return [json.loads(line) for line in fixture_lines(name)]
