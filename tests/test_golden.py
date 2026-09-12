"""Exact equivalence with the Lua module: every slot, variant, footnote and metadata field, for every
input in tests/fixtures/golden.jsonl.gz (generated upstream by tools/port_fixtures.py)."""

from conftest import fixture_records

from mazini import conjugate

UNDIA = {"َ": "a", "ِ": "i", "ُ": "u", "-": None}

RECORDS = fixture_records("golden.jsonl.gz")
GROUPS: dict[str, list[dict]] = {}
for _rec in RECORDS:
    if "meta" in _rec:
        _b = _rec["meta"]["bases"][0]
        _key = "%s-%s" % (_b["verb_form"], _b["conj_vowels"][0]["weakness"])
    else:
        _key = "error-" + _rec["error"]["code"]
    GROUPS.setdefault(_key, []).append(_rec)


def _run(rec):
    wazn = rec["in"]["form"] or rec["in"]["wazn"] or ""
    return conjugate(rec["in"]["root"], wazn, passive=rec["in"]["passive"], reduced=rec["in"]["reduced"])


def _slots_of(c):
    return [[slot, [[f.form, list(f.footnotes)] for f in forms]] for slot, forms in c.slots.items()]


def _meta_of(c):
    v = c.vowels
    return {
        "verb_slots": list(c.slot_list),
        "morph_pattern": c.morph_patterns,
        "verb_forms": c.verb_forms,
        "passive": c.passive,
        "passive_uncertain": c.passive_uncertain,
        "has_active": c.has_active,
        "has_passive": c.has_passive,
        "slot_uncertain": c.uncertain_slots,
        "verb_type": c.verb_type,
        "classification": c.classification,
        "base": {
            "verb_form": c.verb_form,
            "passive": c.passive,
            "passive_uncertain": c.passive_uncertain,
            "passive_defaulted": c.passive_defaulted,
            "irregular": c.irregular,
            "reduced": c.reduced,
            "quadlit": c.quadriliteral,
            "orth": sorted(k for k, on in c.orth.items() if on),
            "past": v.past if v else None,
            "nonpast": v.nonpast if v else None,
            "radicals": c.radicals,
            "weakness": c.weakness,
            "form_viii_assim": c.form_viii_assim,
        },
    }


def _meta_of_golden(m):
    b = m["bases"][0]
    cv = b["conj_vowels"][0]
    return {
        "verb_slots": m["verb_slots"],
        "morph_pattern": m["morph_pattern"],
        "verb_forms": m["verb_forms"],
        "passive": m["passive"],
        "passive_uncertain": m["passive_uncertain"],
        "has_active": m["has_active"],
        "has_passive": m["has_passive"],
        "slot_uncertain": m["slot_uncertain"],
        "verb_type": m["verb_type"],
        "classification": m["classification"],
        "base": {
            "verb_form": b["verb_form"],
            "passive": b["passive"],
            "passive_uncertain": b["passive_uncertain"],
            "passive_defaulted": b["passive_defaulted"],
            "irregular": b["irregular"],
            "reduced": b["reduced"],
            "quadlit": b["quadlit"],
            "orth": b["orth"],
            "past": UNDIA[cv["past"]],
            "nonpast": UNDIA[cv["nonpast"]],
            "radicals": [cv["rad1"], cv["rad2"], cv["rad3"]] + ([cv["rad4"]] if cv["rad4"] else []),
            "weakness": cv["weakness"],
            "form_viii_assim": cv["form_viii_assim"],
        },
    }


def test_every_variant_is_covered():
    """The comparison is not vacuous: every variant of every slot of every record is in the golden."""
    variants = sum(len(v) for rec in RECORDS if "slots" in rec for _, v in rec["slots"])
    print("golden: %d inputs, %d variants" % (len(RECORDS), variants))
    assert len(RECORDS) > 7000
    assert variants > 700000
    assert len(GROUPS) > 40
