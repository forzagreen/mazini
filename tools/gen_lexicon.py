#!/usr/bin/env python3
"""Regenerate the attested-verb lexicon from a checkout of the arabic-morphology dataset.

    python3 tools/gen_lexicon.py --source /path/to/arabic-morphology   # or ARABIC_MORPHOLOGY=...

The dataset (https://github.com/m-bakni/arabic-morphology, CC BY 4.0) is four tables of roots × patterns,
each cell marked ل (لازم, intransitive), م (متعدٍّ, transitive) or ك (both). This script folds them into one
compact string per root length and writes it as a source file, Python or TypeScript by the extension of
--out (default: the data module of the repository the script lives in). No dependencies.

Encoding (also described in the generated file): one root per line. The first 3 (TRI) or 4 (QUAD)
characters are the radicals in Buckwalter transliteration (ROOT_CODES[i] stands for ROOT_LETTERS[i]); each
following character is one attested pattern, SYMBOLS[3 * i + t] where i indexes TRI_WAZNS or QUAD_WAZNS
and t is 0 for لازم, 1 for متعدٍّ, 2 for both. Roots are in Arabic alphabetical order, patterns in table
order. The dataset writes hamza as أ in every seat; roots are stored with ء, as mazini normalises them.
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
SYMBOLS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
TRANS = {"ل": 0, "م": 1, "ك": 2}
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


def read(source: str) -> dict[str, dict[str, int]]:
    """root → {wazn → transitivity code}, from the four tables."""
    verbs: dict[str, dict[str, int]] = {}
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
            entry = verbs.setdefault(root, {})
            for wazn, mark in zip(patterns, row[1 + n :], strict=False):
                mark = mark.strip()
                if not mark:
                    continue
                if mark not in TRANS:
                    sys.exit("unknown mark %r for %s %s" % (mark, root, wazn))
                if wazn in entry:
                    sys.exit("%s %s is listed twice" % (root, wazn))
                entry[wazn] = TRANS[mark]
    return verbs


def encode(verbs: dict[str, dict[str, int]], n: int, wazns: list[str]) -> str:
    order = {ch: i for i, ch in enumerate(ROOT_LETTERS)}
    lines = []
    for root in sorted((r for r in verbs if len(r) == n), key=lambda r: [order[ch] for ch in r]):
        codes = "".join(ROOT_CODES[order[ch]] for ch in root)
        syms = "".join(SYMBOLS[3 * wazns.index(w) + t] for w, t in sorted(verbs[root].items(), key=lambda kv: wazns.index(kv[0])))
        lines.append(codes + syms)
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
        "Format: one root per line. The first 3 (TRI) or 4 (QUAD) characters are the radicals in Buckwalter\n"
        "transliteration (ROOT_CODES[i] stands for ROOT_LETTERS[i]); each following character is one attested\n"
        "pattern, SYMBOLS[3 * i + t], where i indexes TRI_WAZNS or QUAD_WAZNS and t is 0 for لازم, 1 for متعدٍّ,\n"
        "2 for both. Roots are in Arabic alphabetical order, patterns in table order, hamza always ء."
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
            "TRI_WAZNS = (%s)\n"
            "QUAD_WAZNS = (%s)\n"
            'TRI = """\\\n%s"""\n'
            'QUAD = """\\\n%s"""\n'
        ) % (
            doc,
            q(meta["url"]), q(meta["commit"]), q(meta["date"]), meta["roots"], meta["verbs"],
            q(ROOT_LETTERS), q(ROOT_CODES), q(SYMBOLS),
            ", ".join(q(w) for w in TRI_WAZNS) + ",",
            ", ".join(q(w) for w in QUAD_WAZNS) + ",",
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
        % (os.path.relpath(out, REPO), meta["roots"], tri.count("\n"), quad.count("\n"), meta["verbs"], len(tri) + len(quad), meta["commit"][:12])
    )


if __name__ == "__main__":
    main()
