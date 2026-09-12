"""inflect_tense and the stem-pattern conjugators. Port of ar-verb.lua 1242-1440."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .base import Base, add3, stem_or_empty
from .chars import IMP_PERSON_NUMBERS, PERSON_NUMBERS, dia
from .endings import (
    IMP_ENDINGS,
    IMP_ENDINGS_ALT_A,
    IMP_ENDINGS_ALT_I,
    IND_ENDINGS,
    JUSS_ENDINGS,
    JUSS_ENDINGS_ALT_A,
    JUSS_ENDINGS_ALT_I,
    NONPAST_PREFIX_CONSONANTS,
    PAST_ENDINGS,
    SUB_ENDINGS,
    Endings,
)  # fmt: skip
from .errors import internal
from .forms import AbForm, AbForms, combine_form_and_footnotes, q


@dataclass(frozen=True, slots=True)
class AllSame:
    """A single abbreviated form list used for every person."""

    value: AbForms


Affixes = str | AllSame | Sequence[AbForms]


def all_same(x: AbForms) -> AllSame:
    return AllSame(x)


def _get_affix(affixes: Affixes, i: int) -> AbForms:
    if isinstance(affixes, str):
        return affixes
    if isinstance(affixes, AllSame):
        return affixes.value
    return affixes[i]


def _verify(tense: str, name: str, affixes: Affixes, n: int) -> None:
    if not isinstance(affixes, str | AllSame) and len(affixes) != n:
        internal("For tense '%s', '%s' should have length %d but has length %d" % (tense, name, n, len(affixes)))


def inflect_tense_1(
    base: Base,
    tense: str,
    prefixes: Affixes | None,
    stems: Affixes | None,
    endings: Affixes | None,
    pnums: Sequence[str],
) -> None:
    """inflect_tense_1: zip prefixes × stems × endings into `tense_<person>` for every person in `pnums`."""
    if prefixes is None or stems is None or endings is None:
        return
    _verify(tense, "prefixes", prefixes, len(pnums))
    _verify(tense, "stems", stems, len(pnums))
    _verify(tense, "endings", endings, len(pnums))
    for i, pn in enumerate(pnums):
        add3(base, tense + "_" + pn, _get_affix(prefixes, i), _get_affix(stems, i), _get_affix(endings, i))


def inflect_tense(
    base: Base, tense: str, prefixes: Affixes | None, stems: Affixes | None, endings: Affixes | None
) -> None:
    inflect_tense_1(base, tense, prefixes, stems, endings, PERSON_NUMBERS)


def inflect_tense_imp(base: Base, stems: Affixes | None, endings: Affixes | None) -> None:
    inflect_tense_1(base, "imp", "", stems, endings, IMP_PERSON_NUMBERS)


def past_2stem_conj(
    base: Base, tense: str, v_stem: AbForms | None, c_stem: AbForms | None, footnote_12: str | None = None
) -> None:
    """past_2stem_conj: vowel-initial and consonant-initial past stems (sound, assimilated, hollow, geminate)."""
    v = stem_or_empty(v_stem)
    c12: AbForms = stem_or_empty(c_stem)
    if (
        footnote_12 is not None
        and c_stem is not None
        and isinstance(c_stem, str | type(c12))
        and not isinstance(c_stem, list)
    ):
        c12 = combine_form_and_footnotes(c_stem, footnote_12)  # type: ignore[arg-type]
    c3: AbForms = stem_or_empty(c_stem)
    inflect_tense(base, tense, "", [c12, c12, c12, v, v, c12, v, v, c12, c12, c12, v, c3], PAST_ENDINGS)


def past_1stem_conj(base: Base, tense: str, stem: AbForms | None) -> None:
    past_2stem_conj(base, tense, stem, stem)


def _prefix_stem(pv: str, stem: AbForms) -> AbForms:
    """q(dia[prefix_vowel], stem) for a string/form stem, or per element for a list."""
    if isinstance(stem, str) or not isinstance(stem, Sequence):
        return q(pv, stem)  # type: ignore[arg-type]
    return [q(pv, s) for s in stem]


def nonpast_2stem_conj(
    base: Base,
    tense: str,
    prefix_vowel: str,
    v_stem_in: AbForms | None,
    c_stem_in: AbForms | None,
    endings: Endings | None = None,
    jussive: bool = False,
) -> None:
    """nonpast_2stem_conj: non-past with vowel-initial and consonant-initial stems; endings inferred from the tense."""
    pv = dia[prefix_vowel]
    v_stem = stem_or_empty(None if v_stem_in is None else _prefix_stem(pv, v_stem_in))
    c_stem = stem_or_empty(None if c_stem_in is None else _prefix_stem(pv, c_stem_in))
    if endings is None:
        if tense.startswith("ind"):
            endings = IND_ENDINGS
        elif tense.startswith("sub"):
            endings = SUB_ENDINGS
        elif tense.startswith("juss"):
            jussive = True
            endings = JUSS_ENDINGS
        else:
            internal("Unrecognized tense '" + tense + "'")
    if not jussive:
        stems: list[AbForms] = [
            v_stem,
            v_stem,
            v_stem,
            v_stem,
            v_stem,
            v_stem,
            v_stem,
            v_stem,
            v_stem,
            v_stem,
            c_stem,
            v_stem,
            c_stem,
        ]
    else:
        stems = [c_stem, c_stem, v_stem, c_stem, c_stem, v_stem, v_stem, v_stem, c_stem, v_stem, c_stem, v_stem, c_stem]
    inflect_tense(base, tense, NONPAST_PREFIX_CONSONANTS, stems, endings)


def nonpast_1stem_conj(
    base: Base,
    tense: str,
    prefix_vowel: str,
    stem: AbForms | None,
    endings: Endings | None = None,
    jussive: bool = False,
) -> None:
    nonpast_2stem_conj(base, tense, prefix_vowel, stem, stem, endings, jussive)


def jussive_gem_conj(base: Base, tense: str, prefix_vowel: str, v_stem: AbForms | None, c_stem: AbForms | None) -> None:
    """jussive_gem_conj: the three geminate jussive alternants (-a, -i, null)."""
    nonpast_2stem_conj(base, tense, prefix_vowel, v_stem, c_stem, JUSS_ENDINGS_ALT_A)
    nonpast_2stem_conj(base, tense, prefix_vowel, v_stem, c_stem, JUSS_ENDINGS_ALT_I)
    nonpast_2stem_conj(base, tense, prefix_vowel, v_stem, c_stem, JUSS_ENDINGS, True)


def make_2stem_imperative(
    base: Base,
    v_stem_in: AbForms | None,
    c_stem_in: AbForms | None,
    endings: Endings | None = None,
    alt_gem: bool = False,
) -> None:
    endings = endings if endings is not None else IMP_ENDINGS
    v_stem = stem_or_empty(v_stem_in)
    c_stem = stem_or_empty(c_stem_in)
    if alt_gem:
        inflect_tense_imp(base, [v_stem, v_stem, v_stem, v_stem, c_stem], endings)
    else:
        inflect_tense_imp(base, [c_stem, v_stem, v_stem, v_stem, c_stem], endings)


def make_1stem_imperative(base: Base, stem: AbForms | None) -> None:
    make_2stem_imperative(base, stem, stem)


def make_gem_imperative(base: Base, v_stem: AbForms | None, c_stem: AbForms | None) -> None:
    make_2stem_imperative(base, v_stem, c_stem, IMP_ENDINGS_ALT_A, True)
    make_2stem_imperative(base, v_stem, c_stem, IMP_ENDINGS_ALT_I, True)
    make_2stem_imperative(base, v_stem, c_stem)


__all__ = [
    "AbForm", "Affixes", "AllSame", "all_same", "inflect_tense", "inflect_tense_1", "inflect_tense_imp", "jussive_gem_conj",
    "make_1stem_imperative", "make_2stem_imperative", "make_gem_imperative", "nonpast_1stem_conj", "nonpast_2stem_conj",
    "past_1stem_conj", "past_2stem_conj",
]  # fmt: skip
