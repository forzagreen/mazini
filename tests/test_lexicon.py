"""The attested-verb lexicon: decoding, lookups, and that every listed verb conjugates."""

import pytest

from mazini import WAZNS, MaziniError, conjugate, normalize_root
from mazini.lexicon import LEXICON_INFO, attested_wazns, is_attested, lexicon_roots

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


def test_every_attested_verb_conjugates():
    verbs = [(r, w) for r in lexicon_roots() for w in attested_wazns(r)]
    for root, wazn in verbs[::9]:
        c = conjugate(root, wazn)
        assert c.lemma and c.wazn == wazn, (root, wazn)
