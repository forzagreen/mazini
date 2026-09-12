"""loose() parity with the Python reference (which it is a copy of) and the Lua port upstream."""

from conftest import fixture_records

from mazini import loose

SAME = [
    ("أُؤْكَلُ", "أُوكَلُ"),
    ("يُوْصَلُ", "يُوصَلُ"),
    ("اِيْقَظْ", "اِيقَظْ"),
    ("إِيْثِرْ", "اِئْثِرْ"),
    ("إدْ", "إِدْ"),
    ("ٱفْعُلْ", "افْعُلْ"),
    ("فَعَلَا", "فَعَلا"),
    ("يَفْعَلْ", "يَفْعَل"),
]
DISTINCT = [
    ("خُفْتَ", "خِفْتَ"),
    ("يُوصَلُ", "يُوصِلُ"),
    ("يَقُولُ", "يَقِيلُ"),
    ("مُدِدْتُنَّ", "مُدِدْتُنُّ"),
    ("وُصِلَتْ", "وَصِلَتْ"),
    ("يُلَى", "يُولَى"),
    ("إدْ", "أُدْ"),
    ("اِوْنَ", "اِينَ"),
]


def test_loose_parity():
    recs = fixture_records("loose.jsonl.gz")
    assert len(recs) > 50000
    bad = [(r["s"], r["py"], loose(r["s"])) for r in recs if loose(r["s"]) != r["py"]]
    assert bad[:10] == []
    drift = [(r["s"], r["py"], r["lua"]) for r in recs if r["py"] != r["lua"]]
    assert drift[:10] == []


def test_same_and_distinct():
    for a, b in SAME:
        assert loose(a) == loose(b), (a, b)
    for a, b in DISTINCT:
        assert loose(a) != loose(b), (a, b)
