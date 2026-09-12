"""The book: every printed cell of the 462 paradigms, checked as upstream's tests/run.lua checks the module."""

import csv
import os

from conftest import FIXTURES

from mazini import conjugate, loose

COLS = {"past": "past_", "past_pass": "past_pass_", "ind": "ind_", "ind_pass": "ind_pass_", "imp": "imp_"}


def test_every_printed_cell_is_generated():
    book = os.path.join(FIXTURES, "book")
    with open(os.path.join(book, "index.csv"), encoding="utf-8") as f:
        index = list(csv.DictReader(f))
    assert len(index) == 462
    passed = 0
    failed: list[str] = []
    per_column: dict[str, int] = {}
    for e in index:
        c = conjugate(e["root"], e["wazn"], passive=bool(e["passive"]), reduced=bool(e["reduced"]))
        with open(os.path.join(book, e["slug"] + ".csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            for col, prefix in COLS.items():
                expected = row[col]
                if not expected:
                    continue
                slot = prefix + row["person"]
                forms = c.slots.get(slot, [])
                want = loose(expected)
                if any(loose(f.form) == want for f in forms):
                    passed += 1
                    per_column[col] = per_column.get(col, 0) + 1
                else:
                    failed.append(
                        "%s %s: book %s, engine %s"
                        % (e["slug"], slot, expected, " | ".join(f.form for f in forms) or "(none)")
                    )
    print("book: %d passed, %d failed; per column %s" % (passed, len(failed), per_column))
    assert failed[:20] == []
    assert passed == 15549
