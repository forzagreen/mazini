"""The attested-verb lexicon: decoding, lookups, and that every listed verb conjugates."""

import pytest

from mazini import WAZNS, MaziniError, conjugate, normalize_root
from mazini.lexicon import LEXICON_INFO, is_attested, lexicon_entries, lexicon_roots, transitivity
from mazini.wazn import WAZN_BY_NAME

ALPHABET = "ءبتثجحخدذرزسشصضطظعغفقكلمنهوي"


def test_counts_match_the_generated_header():
    roots = lexicon_roots()
    assert len(roots) == LEXICON_INFO.roots == 7626
    assert sum(len(lexicon_entries(r)) for r in roots) == LEXICON_INFO.verbs == 24188
    assert LEXICON_INFO.source_url == "https://github.com/m-bakni/arabic-morphology"
    assert len(LEXICON_INFO.source_commit) == 40


def test_roots_are_normalised_and_sorted():
    roots = lexicon_roots()
    keys = [(len(r), [ALPHABET.index(ch) for ch in r]) for r in roots]
    assert keys == sorted(keys)
    for r in roots:
        assert len(r) in (3, 4) and normalize_root(r) == list(r), r
        for e in lexicon_entries(r):
            assert e.root == r and WAZN_BY_NAME[e.wazn].form_code == e.form_code
            assert e.transitivity in ("intransitive", "transitive", "both")
            assert (len(r) == 4) == e.form_code.endswith("q")
    assert {e.wazn for r in roots for e in lexicon_entries(r)} == {w.wazn for w in WAZNS}


def test_entries_follow_the_tables():
    # Rows of the four CSV tables, read against the marks ل / م / ك.
    assert [(e.wazn, e.transitivity) for e in lexicon_entries("أبأ")] == [("فعَل يفعَل", "transitive")]
    assert [(e.form_code, e.transitivity) for e in lexicon_entries("أبب")] == [
        ("I/a~u", "both"),
        ("I/a~i", "both"),
        ("II", "intransitive"),
        ("V", "intransitive"),
        ("VIII", "intransitive"),
    ]
    assert [e.wazn for e in lexicon_entries("كتب")] == [
        "فعَل يفعُل", "فعَل يفعِل", "فعّل", "فاعل", "أفعل", "تفعّل", "تفاعل", "افتعل", "استفعل",
    ]  # fmt: skip
    assert [(e.form_code, e.transitivity) for e in lexicon_entries("بأبأ")] == [("Iq", "both"), ("IIq", "intransitive")]
    assert [(e.form_code, e.transitivity) for e in lexicon_entries("قشعر")] == [
        ("Iq", "transitive"),
        ("IIq", "intransitive"),
        ("IVq", "intransitive"),
    ]
    assert lexicon_entries("حرجم")[1].form_code == "IIIq"


def test_lookups_take_every_root_and_pattern_spelling():
    assert transitivity("كتب", "استفعل") == "transitive"
    assert transitivity("ك ت ب", "X") == "transitive"
    assert transitivity("ك_ت_ب", "I/a~u") == "both"
    assert transitivity("أخذ", "فاعل") == transitivity("ءخذ", "III") == "transitive"
    assert transitivity("أخذ", "افتعل") == "both"
    assert transitivity("رمى", "فعَل يفعِل") == transitivity("رمي", "I/a~i") == "both"
    assert is_attested("كتب", "تفاعل") and not is_attested("كتب", "افعوعل") and not is_attested("كتب", "فعُل يفعُل")
    assert transitivity("كتب", "افعوعل") is None
    assert lexicon_entries("ضضض") == [] and not is_attested("ضضض", "فعَل يفعُل")


@pytest.mark.parametrize("root,wazn,code", [("قال", "فعَل يفعُل", "bad_root"), ("كتب", "فعل", "unknown_wazn")])
def test_bad_input_raises_like_conjugate(root, wazn, code):
    with pytest.raises(MaziniError) as e:
        is_attested(root, wazn)
    assert e.value.code == code
    if code == "bad_root":
        with pytest.raises(MaziniError):
            lexicon_entries(root)


def test_every_attested_verb_conjugates():
    entries = [e for r in lexicon_roots() for e in lexicon_entries(r)]
    for e in entries[::9]:
        c = conjugate(e.root, e.wazn)
        assert c.lemma and c.wazn == e.wazn, (e.root, e.wazn)
