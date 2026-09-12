"""Command line: `mazini كتب "فعَل يفعُل" [--passive] [--reduced] [--json]`."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from . import WAZNS, MaziniError, conjugate
from .chars import IMP_PERSON_NUMBERS, PERSON_NUMBERS

_PERSON_AR = {
    "3ms": "هو", "3md": "هما", "3mp": "هم", "3fs": "هي", "3fd": "هما (مؤ)", "3fp": "هنّ",
    "2ms": "أنتَ", "2d": "أنتما", "2mp": "أنتم", "2fs": "أنتِ", "2fp": "أنتنّ", "1s": "أنا", "1p": "نحن",
}  # fmt: skip
_ORDER = ["3ms", "3md", "3mp", "3fs", "3fd", "3fp", "2ms", "2d", "2mp", "2fs", "2fp", "1s", "1p"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mazini", description="Conjugate an Arabic verb from its root and pattern.")
    ap.add_argument("root", nargs="?", help="three or four radicals, e.g. كتب or ك_ت_ب")
    ap.add_argument("wazn", nargs="?", help="pattern name (فعَل يفعُل, استفعل) or form code (I/a~u, X)")
    ap.add_argument("--passive", action="store_true", help="|مبني للمجهول=: full personal passive")
    ap.add_argument("--reduced", action="store_true", help="|مدغم=: assimilated affix")
    ap.add_argument("--json", action="store_true", help="print the full result as JSON")
    ap.add_argument("--list-wazn", action="store_true", help="list the 22 patterns and exit")
    args = ap.parse_args(argv)

    if args.list_wazn:
        for w in WAZNS:
            print("%-12s %-7s %s" % (w.wazn, w.form_code, w.basic_deriv))
        return 0
    if not args.root or not args.wazn:
        ap.error("root and wazn are required")
    try:
        c = conjugate(args.root, args.wazn, passive=args.passive, reduced=args.reduced)
    except MaziniError as e:
        print("error (%s): %s" % (e.code, e), file=sys.stderr)
        return 1
    if args.json:
        d = asdict(c)
        d.pop("_extra", None)
        d["slots"] = {k: [{"form": f.form, "footnotes": list(f.footnotes)} for f in v] for k, v in c.slots.items()}
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return 0

    def cell(slot: str) -> str:
        return " / ".join(f.form for f in c.slots.get(slot, [])) or "—"

    print("%s — %s — %s" % (cell("past_3ms"), c.root_display, c.verb_type))
    print("المصدر: %s   اسم الفاعل: %s   اسم المفعول: %s" % (cell("vn"), cell("ap"), cell("pp")))
    print()
    cols = [("past_", "الماضي"), ("ind_", "المضارع"), ("sub_", "المنصوب"), ("juss_", "المجزوم"), ("imp_", "الأمر")]
    print("%-10s" % "" + "".join("%-22s" % label for _, label in cols))
    for p in _ORDER:
        row = "%-10s" % _PERSON_AR[p]
        for prefix, _ in cols:
            row += "%-22s" % (cell(prefix + p) if prefix != "imp_" or p in IMP_PERSON_NUMBERS else "")
        print(row)
    if c.has_passive and any("_pass_" in s for s in c.slots):
        print()
        pcols = [
            ("past_pass_", "الماضي المجهول"),
            ("ind_pass_", "المضارع المجهول"),
            ("sub_pass_", "المنصوب"),
            ("juss_pass_", "المجزوم"),
        ]
        print("%-10s" % "" + "".join("%-22s" % label for _, label in pcols))
        for p in _ORDER:
            print("%-10s" % _PERSON_AR[p] + "".join("%-22s" % cell(prefix + p) for prefix, _ in pcols))
    assert PERSON_NUMBERS
    return 0


if __name__ == "__main__":
    sys.exit(main())
