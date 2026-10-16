#!/usr/bin/env python3
"""Regenerate the attested-verb lexicon from a checkout of the arabic-morphology dataset.

    python3 tools/gen_lexicon.py --source /path/to/arabic-morphology   # or ARABIC_MORPHOLOGY=...

The dataset (https://github.com/m-bakni/arabic-morphology, CC BY 4.0) is four tables of roots × patterns,
a cell marked (ل, م or ك: the verb's transitivity, which is not kept) where the verb exists. This script folds
them into one compact string per root length and writes it as a source file, Python or TypeScript by the
extension of --out (default: the data module of the repository the script lives in). No dependencies.

Encoding (also described in the generated file): fixed-width records, newlines ignored. A record is the
radicals in Buckwalter transliteration (ROOT_CODES[i] stands for ROOT_LETTERS[i]) followed by a bitmask of
the attested patterns, bit i for TRI_WAZNS[i] or QUAD_WAZNS[i], written in base 64 (SYMBOLS), most
significant digit first: 3 letters + 3 digits for a triliteral root, 4 letters + 1 digit for a quadriliteral.
Roots are in Arabic alphabetical order. The dataset writes hamza as أ in every seat; roots are stored with
ء, as mazini normalises them.
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SOURCE_URL = "https://github.com/m-bakni/arabic-morphology"

ROOT_LETTERS = "ءبتثجحخدذرزسشصضطظعغفقكلمنهوي"
ROOT_CODES = "'btvjHxd*rzs$SDTZEgfqklmnhwy"
SYMBOLS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"
MARKS = {"ل", "م", "ك"}  # لازم, متعدٍّ, both: the verb exists either way
RECORDS_PER_LINE = 16
HAMZA_SEATS = {"أ": "ء", "إ": "ء", "آ": "ء", "ؤ": "ء", "ئ": "ء", "ى": "ي"}

# The 22 patterns, in the order mazini's WAZNS lists them (src/mazini/wazn.py, src/wazn.ts).
TRI_WAZNS = [
    "فعَل يفعُل", "فعَل يفعِل", "فعَل يفعَل", "فعُل يفعُل", "فعِل يفعَل", "فعِل يفعِل",
    "فعّل", "فاعل", "أفعل", "تفعّل", "تفاعل", "انفعل", "افتعل", "افعلّ", "استفعل", "افعالّ", "افعوعل", "افعوّل",
]  # fmt: skip
QUAD_WAZNS = ["فعلل", "تفعلل", "افعنلل", "افعللّ"]

TABLES = [  # (file, radicals, pattern list)
    ("جدول الأفعال الثلاثية المجردة.csv", 3, TRI_WAZNS),
    ("جدول الأفعال الثلاثية المزيدة.csv", 3, TRI_WAZNS),
    ("جدول الأفعال الرباعية المجردة.csv", 4, QUAD_WAZNS),
    ("جدول الأفعال الرباعية المزيدة.csv", 4, QUAD_WAZNS),
]


def pattern_name(header: str, known: list[str]) -> str:
    """A table column as mazini names the pattern: only فَعْلَلَ differs (by its vowel marks)."""
    if header in known:
        return header
    bare = "".join(ch for ch in header if not unicodedata.combining(ch))
    if bare in known:
        return bare
    sys.exit("unknown pattern column %r" % header)


def normalize_root(raw: str, n: int) -> str:
    root = "".join(HAMZA_SEATS.get(ch, ch) for ch in raw if not unicodedata.combining(ch))
    if len(root) != n or any(ch not in ROOT_LETTERS for ch in root):
        sys.exit("bad %d-radical root %r" % (n, raw))
    return root


def read(source: str) -> dict[str, set[str]]:
    """root → its attested patterns, from the four tables."""
    verbs: dict[str, set[str]] = {}
    for name, n, known in TABLES:
        path = os.path.join(source, "data", "csv", name)
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
        header, body = rows[0], rows[1:]
        if len(header) < 1 + n + 1:
            sys.exit("unexpected header in " + name)
        patterns = [pattern_name(h, known) for h in header[1 + n :]]
        for row in body:
            if not row or not row[0].strip():
                continue
            root = normalize_root(row[0].strip(), n)
            if "".join(row[1 : 1 + n]) != row[0].strip():
                sys.exit("radical columns disagree with the root in %r" % row)
            entry = verbs.setdefault(root, set())
            for wazn, mark in zip(patterns, row[1 + n :], strict=False):
                mark = mark.strip()
                if not mark:
                    continue
                if mark not in MARKS:
                    sys.exit("unknown mark %r for %s %s" % (mark, root, wazn))
                if wazn in entry:
                    sys.exit("%s %s is listed twice" % (root, wazn))
                entry.add(wazn)
    return verbs


def encode(verbs: dict[str, set[str]], n: int, wazns: list[str]) -> str:
    """Fixed-width records (radicals + base-64 bitmask), RECORDS_PER_LINE to a line for the sake of diffs."""
    order = {ch: i for i, ch in enumerate(ROOT_LETTERS)}
    digits = (len(wazns) + 5) // 6
    records = []
    for root in sorted((r for r in verbs if len(r) == n), key=lambda r: [order[ch] for ch in r]):
        mask = sum(1 << wazns.index(w) for w in verbs[root])
        bits = "".join(SYMBOLS[(mask >> (6 * d)) & 63] for d in reversed(range(digits)))
        records.append("".join(ROOT_CODES[order[ch]] for ch in root) + bits)
    lines = ["".join(records[i : i + RECORDS_PER_LINE]) for i in range(0, len(records), RECORDS_PER_LINE)]
    return "\n".join(lines) + "\n"


def git(source: str, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", source, *args], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def render(lang: str, meta: dict[str, object], tri: str, quad: str) -> str:
    doc = (
        "Attested-verb lexicon data, GENERATED by tools/gen_lexicon.py; do not edit.\n"
        "\n"
        "Source: %(url)s @ %(commit)s (%(date)s), the four root × pattern tables of جداول إحصاء الأفعال العربية\n"
        "(مروان البواب ويحيى مير علم), CC BY 4.0. %(verbs)d verbs over %(roots)d roots.\n"
        "\n"
        "Format: fixed-width records, newlines ignored. A record is the radicals in Buckwalter transliteration\n"
        "(ROOT_CODES[i] stands for ROOT_LETTERS[i]) followed by a bitmask of the attested patterns, bit i for\n"
        "TRI_WAZNS[i] or QUAD_WAZNS[i], in base 64 (SYMBOLS) most significant digit first: 3 letters + 3 digits\n"
        "per triliteral root (TRI), 4 letters + 1 digit per quadriliteral (QUAD). Roots are in Arabic\n"
        "alphabetical order, hamza always ء."
    ) % meta
    if lang == "py":
        q = lambda s: '"%s"' % s  # noqa: E731
        return (
            '"""%s\n"""\n\n'
            "SOURCE_URL = %s\n"
            "SOURCE_COMMIT = %s\n"
            "SOURCE_DATE = %s\n"
            "ROOT_COUNT = %d\n"
            "VERB_COUNT = %d\n"
            "ROOT_LETTERS = %s\n"
            "ROOT_CODES = %s\n"
            "SYMBOLS = %s\n"
            "TRI_WAZNS = (\n%s)\n"
            "QUAD_WAZNS = (\n%s)\n"
            'TRI = """\\\n%s"""\n'
            'QUAD = """\\\n%s"""\n'
        ) % (
            doc,
            q(meta["url"]), q(meta["commit"]), q(meta["date"]), meta["roots"], meta["verbs"],
            q(ROOT_LETTERS), q(ROOT_CODES), q(SYMBOLS),
            "".join("    %s,\n" % q(w) for w in TRI_WAZNS),
            "".join("    %s,\n" % q(w) for w in QUAD_WAZNS),
            tri, quad,
        )  # fmt: skip
    return (
        "// %s\n"
        "export const SOURCE_URL = %s;\n"
        "export const SOURCE_COMMIT = %s;\n"
        "export const SOURCE_DATE = %s;\n"
        "export const ROOT_COUNT = %d;\n"
        "export const VERB_COUNT = %d;\n"
        "export const ROOT_LETTERS = %s;\n"
        "export const ROOT_CODES = %s;\n"
        "export const SYMBOLS = %s;\n"
        "export const TRI_WAZNS: readonly string[] = [\n%s];\n"
        "export const QUAD_WAZNS: readonly string[] = [%s];\n"
        "export const TRI = `\n%s`;\n"
        "export const QUAD = `\n%s`;\n"
    ) % (
        "\n".join("// " + line if line else "//" for line in doc.split("\n")).removeprefix("// "),
        _js(meta["url"]), _js(meta["commit"]), _js(meta["date"]), meta["roots"], meta["verbs"],
        _js(ROOT_LETTERS), _js(ROOT_CODES), _js(SYMBOLS),
        "".join("  %s,\n" % _js(w) for w in TRI_WAZNS),
        ", ".join(_js(w) for w in QUAD_WAZNS),
        tri, quad,
    )  # fmt: skip


def _js(s: object) -> str:
    return '"%s"' % s


def default_out() -> str:
    for cand in ("src/mazini/_lexicon_data.py", "src/lexicon-data.ts"):
        if os.path.isdir(os.path.join(REPO, os.path.dirname(cand))):
            return os.path.join(REPO, cand)
    sys.exit("cannot tell which repository this is; pass --out")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--source",
        default=os.environ.get("ARABIC_MORPHOLOGY") or os.path.join(os.path.dirname(REPO), "arabic-morphology"),
        help="checkout of the arabic-morphology dataset (or set ARABIC_MORPHOLOGY)",
    )
    ap.add_argument("--out", help="file to write; .py or .ts (default: this repository's data module)")
    args = ap.parse_args()
    source = os.path.abspath(args.source)
    if not os.path.isdir(os.path.join(source, "data", "csv")):
        ap.error("no data/csv under " + source)
    out = os.path.abspath(args.out or default_out())
    lang = "py" if out.endswith(".py") else "ts" if out.endswith(".ts") else ap.error("--out must end in .py or .ts")

    verbs = read(source)
    meta = {
        "url": SOURCE_URL,
        "commit": git(source, "rev-parse", "HEAD") or "unknown",
        "date": git(source, "log", "-1", "--format=%cs") or "unknown",
        "roots": len(verbs),
        "verbs": sum(len(v) for v in verbs.values()),
        "tri": sum(len(r) == 3 for r in verbs),
        "quad": sum(len(r) == 4 for r in verbs),
    }
    tri = encode(verbs, 3, TRI_WAZNS)
    quad = encode(verbs, 4, QUAD_WAZNS)
    text = render(lang, meta, tri, quad)
    if any(ord(ch) > 127 for ch in tri + quad):
        sys.exit("the encoded tables must be ASCII")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(
        "%s: %d roots (%d triliteral, %d quadriliteral), %d verbs, %d bytes of tables, source %s"
        % (
            os.path.relpath(out, REPO),
            meta["roots"],
            meta["tri"],
            meta["quad"],
            meta["verbs"],
            len(tri) + len(quad),
            meta["commit"][:12],
        )
    )


if __name__ == "__main__":
    main()
