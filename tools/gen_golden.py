#!/usr/bin/env python3
"""Regenerate tests/fixtures/ from the ar-wiktionary-modules checkout.

    python3 tools/gen_golden.py [--ar-verb ../ar-wiktionary-modules]

The committed fixtures are what the test suite checks against; this only needs
rerunning when the upstream corpus or Lua module changes. Needs luajit (or LUA=...)
with luautf8 on LUA_CPATH -- `eval "$(luarocks --lua-version=5.1 path)"` first.
"""

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ar-verb", default=os.path.join(ROOT, "..", "ar-wiktionary-modules"))
    args = ap.parse_args()
    src = os.path.abspath(args.ar_verb)
    script = os.path.join(src, "tools", "port_fixtures.py")
    if not os.path.exists(script):
        sys.exit("not an ar-wiktionary-modules checkout: " + src)
    subprocess.run([sys.executable, script, "--out", os.path.join(ROOT, "tests", "fixtures")], cwd=src, check=True)


if __name__ == "__main__":
    main()
