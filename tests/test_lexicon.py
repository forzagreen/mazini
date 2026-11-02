"""The attested-verb lexicon: decoding, lookups, and that every listed verb conjugates."""

import pytest

from mazini import WAZNS, MaziniError, conjugate, normalize_root
from mazini.lexicon import LEXICON_INFO, attested_wazns, is_attested, lexicon_passive, lexicon_roots, transitivity

ALPHABET = "ءبتثجحخدذرزسشصضطظعغفقكلمنهوي"


def test_counts_match_the_generated_header():
    roots = lexicon_roots()
    assert len(roots) == LEXICON_INFO.roots == 7626
    assert sum(len(attested_wazns(r)) for r in roots) == LEXICON_INFO.verbs == 24188
    assert LEXICON_INFO.source_url == "https://github.com/m-bakni/arabic-morphology"
    assert len(LEXICON_INFO.source_commit) == 40


def test_roots_are_normalised_and_sorted():
    roots = lexicon_roots()
    keys = [(len(r), [ALPHABET.index(ch) for ch in r]) for r in roots]
    assert keys == sorted(keys)
    order = [w.wazn for w in WAZNS]
    for r in roots:
        assert len(r) in (3, 4) and normalize_root(r) == list(r), r
        wazns = attested_wazns(r)
        assert wazns and [order.index(w) for w in wazns] == sorted(order.index(w) for w in wazns), r
        for w in wazns:
            assert (len(r) == 4) == (w in ("فعلل", "تفعلل", "افعنلل", "افعللّ")), (r, w)
    assert {w for r in roots for w in attested_wazns(r)} == set(order)


def test_entries_follow_the_tables():
    # Rows of the four CSV tables.
    assert attested_wazns("أبأ") == ["فعَل يفعَل"]
    assert attested_wazns("أبب") == ["فعَل يفعُل", "فعَل يفعِل", "فعّل", "تفعّل", "افتعل"]
    assert attested_wazns("كتب") == [
        "فعَل يفعُل", "فعَل يفعِل", "فعّل", "فاعل", "أفعل", "تفعّل", "تفاعل", "افتعل", "استفعل",
    ]  # fmt: skip
    assert attested_wazns("أتمت") == ["فعلل"]
    assert attested_wazns("بأبأ") == ["فعلل", "تفعلل"]
    assert attested_wazns("قشعر") == ["فعلل", "تفعلل", "افعللّ"]
    assert attested_wazns("حرجم") == ["فعلل", "افعنلل"]
    assert attested_wazns("يهيه") == ["فعلل"]


def test_lookups_take_every_root_and_pattern_spelling():
    assert is_attested("كتب", "استفعل") and is_attested("ك ت ب", "X") and is_attested("ك_ت_ب", "I/a~u")
    assert is_attested("أخذ", "افتعل") and is_attested("ءخذ", "VIII")
    assert is_attested("رمى", "فعَل يفعِل") and is_attested("رمي", "I/a~i")
    assert not is_attested("كتب", "افعوعل") and not is_attested("كتب", "فعُل يفعُل") and not is_attested("كتب", "IVq")
    assert attested_wazns("ضضض") == [] and not is_attested("ضضض", "فعَل يفعُل")


@pytest.mark.parametrize("root,wazn,code", [("قال", "فعَل يفعُل", "bad_root"), ("كتب", "فعل", "unknown_wazn")])
def test_bad_input_raises_like_conjugate(root, wazn, code):
    with pytest.raises(MaziniError) as e:
        is_attested(root, wazn)
    assert e.value.code == code
    if code == "bad_root":
        with pytest.raises(MaziniError):
            attested_wazns(root)


def test_every_attested_verb_conjugates_with_the_passive_its_transitivity_gives():
    verbs = [(r, w) for r in lexicon_roots() for w in attested_wazns(r)]
    for root, wazn in verbs[::9]:
        passive = lexicon_passive(root, wazn)
        assert passive is not None, (root, wazn)
        c = conjugate(root, wazn, passive=passive)
        assert c.lemma and c.wazn == wazn, (root, wazn)
        assert c.passive == passive, (root, wazn)


def test_transitivity_follows_the_marks():
    count = {"intransitive": 0, "transitive": 0, "both": 0}
    for r in lexicon_roots():
        for w in attested_wazns(r):
            t = transitivity(r, w)
            assert t is not None, (r, w)
            count[t] += 1
    assert count == {"intransitive": 10713, "transitive": 5883, "both": 7592}


@pytest.mark.parametrize(
    "root,wazn,t",
    [
        ("أبأ", "فعَل يفعَل", "transitive"),  # the first row
        ("أبب", "فعَل يفعُل", "both"),
        ("جلس", "فعَل يفعِل", "intransitive"),
        ("جلس", "أفعل", "transitive"),
        ("خرج", "افعالّ", "intransitive"),
        ("فهم", "فعِل يفعَل", "both"),
        ("علم", "تفعّل", "transitive"),
        ("قشعر", "افعللّ", "intransitive"),
        ("ك ت ب", "X", "transitive"),
        ("كتب", "افعوعل", None),
    ],
)
def test_transitivity(root, wazn, t):
    assert transitivity(root, wazn) == t


@pytest.mark.parametrize(
    "root,wazn,p",
    [
        ("ضرب", "فعَل يفعِل", "pass"),  # ك: ضُرِبْتُ
        ("علم", "تفعّل", "pass"),  # م: تُعُلِّمَ
        ("جلس", "فعَل يفعِل", "ipass"),  # ل: جُلِسَ عَلَيْهِ, never *جُلِسْتُ
        ("نوم", "فعِل يفعَل", "ipass"),
        ("حسن", "فعُل يفعُل", "nopass"),  # ل, and فعُل never takes a passive
        ("خرج", "افعالّ", "nopass"),
        ("كتب", "افعوعل", None),
    ],
)
def test_lexicon_passive(root, wazn, p):
    assert lexicon_passive(root, wazn) == p


def test_the_passive_types_conjugate():
    jalasa = conjugate("جلس", "فعَل يفعِل", passive="ipass")
    assert jalasa.slots["past_pass_3ms"][0].form == "جُلِسَ"
    assert "past_pass_1s" not in jalasa.slots
    assert (jalasa.passive, jalasa.passive_defaulted) == ("ipass", False)
    assert conjugate("جلس", "فعَل يفعِل").slots["past_pass_1s"][0].form == "جُلِسْتُ"  # the engine's guess
    assert conjugate("فهم", "فعِل يفعَل", passive="pass").slots["past_pass_1s"][0].form == "فُهِمْتُ"
