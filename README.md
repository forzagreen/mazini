# mazini

[![PyPI](https://img.shields.io/pypi/v/mazini)](https://pypi.org/project/mazini/)
[![CI](https://github.com/forzagreen/mazini/actions/workflows/ci.yml/badge.svg)](https://github.com/forzagreen/mazini/actions/workflows/ci.yml)

**Arabic verb conjugator for Python.** Give it a root and a pattern (وزن) and it returns every form of
the verb: the past, the three non-past moods, the imperative, active and passive, in all thirteen
persons, plus the participles and the مصدر — 119 slots, fully vocalised, with the attested alternative
spellings where Arabic has them.

It is a pure-Python port of Arabic Wiktionary's conjugation engine,
[`وحدة:ar-verb`](https://ar.wiktionary.org/wiki/وحدة:ar-verb) (itself descended from
[`Module:ar-verb`](https://en.wiktionary.org/wiki/Module:ar-verb) on English Wiktionary), and it is
verified two ways:

- **Against the book.** Every one of the **15,549 printed forms** of the 462 paradigms in
  أنطوان الدحداح, *معجم تصريف الأفعال العربية* — the reference work on the subject, transcribed and
  published as the [`ar-conjugation`](https://github.com/forzagreen/ar-conjugation) dataset — is among the forms
  the engine generates.
- **Against the original.** For **7,851 inputs** (every root × pattern combination of a 154-root grid,
  plain, passive and assimilated, plus every book verb) the output is **byte-identical** to the Lua
  module's: 741,188 forms, footnotes and metadata fields, and the same 201 rejected inputs.

- **Pure Python, zero dependencies, no data files.** Python 3.11+. Typed.

> Named after **أبو عثمان المازني** (Abū ʿUthmān al-Māzinī, d. 863), whose كتاب التصريف is the first
> standalone treatise on Arabic morphology.

A JavaScript/TypeScript port with the same API and the same tests, and a live demo:
[`mazini-js`](https://github.com/forzagreen/mazini-js) — **[forzagreen.github.io/mazini-js](https://forzagreen.github.io/mazini-js/)**.

## Install

```bash
pip install mazini
```

## Usage

```python
from mazini import conjugate

v = conjugate("كتب", "فعَل يفعُل")
v.slots["past_3ms"][0].form  # "كَتَبَ"
v.slots["ind_3ms"][0].form  # "يَكْتُبُ"
v.slots["imp_2fs"][0].form  # "اُكْتُبِي"
v.slots["ap"][0].form  # "كَاتِب"
v.verb_type  # "فعل ثلاثي مُجرَّد صحيح سالم"

# A pattern can be given by its Arabic name or its form code; both take the same options.
conjugate("قول", "أفعل").slots["past_3ms"][0].form  # "أَقَالَ"
conjugate("علم", "V").slots["vn"][0].form  # "تَعَلُّم"
conjugate("كتب", "I", vowels=("a", "u"))  # same as "فعَل يفعُل"

# Two switches, the same ones {{تصريف}} takes on the wiki:
conjugate("أخذ", "افتعل", reduced=True).slots["past_3ms"][0].form  # "اِتَّخَذَ" (assimilated affix)
conjugate("علم", "فعِل يفعَل", passive=True)  # a full personal passive for a verb the engine would default to impersonal
```

The result's `slots` maps a slot name (`past_3ms`, `ind_pass_2fp`, `juss_1p`, `imp_2fp`, `ap`, `pp`,
`vn`, …) to the list of forms for that slot, each `Form(form, footnotes)`; a slot the verb lacks is absent.
Alongside it: `lemma`, `verb_form`, `wazn`, `radicals`, `weakness`, `passive` (the passive type),
`irregular`, `morph_patterns`, `has_active` / `has_passive`, `uncertain_slots` (slots shown as `"?"`, i.e.
a form-I مصدر or participle the root alone cannot predict), `verb_type` and `classification`.

Roots may be written `كتب`, `ك ت ب` or `ك_ت_ب`; hamza seats fold to `ء` and `ى` to `ي`. Bad input raises
`MaziniError`, whose `.code` is stable (`bad_root`, `unknown_wazn`, `reduced_not_applicable`, …).

```python
from mazini import WAZNS, SLOTS, classify_triliteral_verb, loose

WAZNS  # the 22 patterns: name, form code, vowels, مجرد/مزيد class
classify_triliteral_verb("ق", "و", "ل")  # "معتل أجوف واوي"
loose("فَعَلَا") == loose("فَعَلا")  # the comparison the book tests use
```

Command line:

```bash
mazini كتب "فعَل يفعُل"            # the table
mazini أخذ افتعل --reduced --json  # everything, as JSON
mazini --list-wazn
```

## What it does not do (yet)

It conjugates from a root and a pattern, which is what every caller on Arabic Wiktionary does. The Lua
module can also take a written, vocalised verb and infer its root (`infer_radicals`), accept per-slot
overrides, and render the wikitext table; none of that is ported. The subjunctive, jussive, participles
and مصدر are generated but are outside the book's tables, so they are verified only against the Lua
module, not against print.

## Development

```bash
uv sync
uv run pytest -q          # hamza, book, golden, loose, api
uv run ruff check
python3 tools/gen_golden.py   # regenerate tests/fixtures/ from ../ar-wiktionary-modules (needs luajit)
```

`tests/fixtures/` is generated upstream by
[`ar-wiktionary-modules`](https://github.com/forzagreen/ar-wiktionary-modules)' `tools/port_fixtures.py`:
`golden.jsonl.gz` (the module's output for 7,851 inputs), `hamza.jsonl.gz` (every hamza-seating call it
made), `loose.jsonl.gz` (the normaliser's parity set), `book/` (the 462 paradigms as CSV) and
`MANIFEST.json` (the upstream commit). The source is ported file for file from `mazini-js`, which was
ported from the Lua; the three keep the same function names and the Lua line references.
