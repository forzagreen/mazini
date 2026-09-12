"""Ending tables for every tense. Port of ar-verb.lua 997-1226.

Lists are 13 long (PERSON_NUMBERS order) or 5 long (IMP_PERSON_NUMBERS order); an empty list in
a cell means "no form for this person".
"""

from __future__ import annotations

from .chars import (
    AA,
    AAMAQ,
    AANI,
    ALIF,
    AW,
    AWSK,
    AY,
    AYSK,
    HAMZA,
    II,
    IMP_PERSON_NUMBERS,
    NA,
    SH,
    SK,
    TA,
    TU,
    UU,
    A,
    I,
    N,
    T,
    U,
    Y,
    imp_index,
    pn_index,
)  # fmt: skip
from .forms import AbForms

Endings = list[AbForms]

#: The 13 endings of the sound/hollow/geminate past tense.
PAST_ENDINGS: Endings = [
    # singular
    SK + TU, SK + TA, SK + "تِ", A, A + "تْ",
    # dual
    SK + "تُمَا", AA, A + "تَا",
    # plural
    SK + "نَا", SK + "تُمْ",
    # šadda + vowel kept in this order on purpose (the module works šadda-first)
    SK + "تُن" + SH + A, UU + ALIF, SK + "نَ",
]  # fmt: skip


def _make_past_endings_ay_aw(ayaw: str, third_sg_masc: str) -> Endings:
    return [
        ayaw + SK + TU, ayaw + SK + TA, ayaw + SK + "تِ", third_sg_masc, A + "تْ",
        ayaw + SK + "تُمَا", ayaw + AA, A + "تَا",
        ayaw + SK + "نَا", ayaw + SK + "تُمْ",
        ayaw + SK + "تُن" + SH + A, AW + SK + ALIF, ayaw + SK + "نَ",
    ]  # fmt: skip


PAST_ENDINGS_AY = _make_past_endings_ay_aw(AY, AAMAQ)
PAST_ENDINGS_AW = _make_past_endings_ay_aw(AW, AA)

#: Alternative endings for form-X geminate verbs like اِسْتَمَرَّ: first and second persons only.
PAST_ENDINGS_AY_12_PERSON_ONLY: Endings = [
    AY + SK + TU, AY + SK + TA, AY + SK + "تِ", [], [],
    AY + SK + "تُمَا", [], [],
    AY + SK + "نَا", AY + SK + "تُمْ",
    AY + SK + "تُن" + SH + A, [], [],
]  # fmt: skip


def _make_past_endings_ii_uu(iiuu: str) -> Endings:
    return [
        iiuu + TU, iiuu + TA, iiuu + "تِ", iiuu + A, iiuu + A + "تْ",
        iiuu + "تُمَا", iiuu + AA, iiuu + A + "تَا",
        iiuu + "نَا", iiuu + "تُمْ",
        iiuu + "تُن" + SH + A, UU + ALIF, iiuu + "نَ",
    ]  # fmt: skip


PAST_ENDINGS_II = _make_past_endings_ii_uu(II)
PAST_ENDINGS_UU = _make_past_endings_ii_uu(UU)

#: The consonant of the non-past prefix, per person.
NONPAST_PREFIX_CONSONANTS: list[str] = [HAMZA, T, T, Y, T, T, Y, T, N, T, T, Y, Y]


def make_nonpast_endings(nul: AbForms, fem: AbForms, dual: AbForms, pl: AbForms, fempl: AbForms) -> Endings:
    """There are only five distinct endings in all non-past verbs."""
    return [nul, nul, fem, nul, nul, dual, dual, dual, nul, pl, fempl, pl, fempl]


IND_ENDINGS = make_nonpast_endings(U, II + NA, AANI, UU + NA, SK + NA)


def _make_sub_juss_endings(dia_null: str) -> Endings:
    return make_nonpast_endings(dia_null, II, AA, UU + ALIF, SK + NA)


SUB_ENDINGS = _make_sub_juss_endings(A)
JUSS_ENDINGS = _make_sub_juss_endings(SK)
#: alternative geminate jussive in -a; same as the subjunctive
JUSS_ENDINGS_ALT_A = SUB_ENDINGS
#: alternative geminate jussive in -i
JUSS_ENDINGS_ALT_I = _make_sub_juss_endings(I)

IND_ENDINGS_AA = make_nonpast_endings(AAMAQ, AYSK + NA, AY + AANI, AWSK + NA, AYSK + NA)


def _make_ind_endings_ii_uu(iiuu: str) -> Endings:
    return make_nonpast_endings(iiuu, II + NA, iiuu + AANI, UU + NA, iiuu + NA)


IND_ENDINGS_II = _make_ind_endings_ii_uu(II)
IND_ENDINGS_UU = _make_ind_endings_ii_uu(UU)

SUB_ENDINGS_AA = make_nonpast_endings(AAMAQ, AYSK, AY + AA, AWSK + ALIF, AYSK + NA)


def _make_sub_endings_ii_uu(iiuu: str) -> Endings:
    return make_nonpast_endings(iiuu + A, II, iiuu + AA, UU + ALIF, iiuu + NA)


SUB_ENDINGS_II = _make_sub_endings_ii_uu(II)
SUB_ENDINGS_UU = _make_sub_endings_ii_uu(UU)

JUSS_ENDINGS_AA = make_nonpast_endings(A, AYSK, AY + AA, AWSK + ALIF, AYSK + NA)


def _make_juss_endings_ii_uu(iu: str, iiuu: str) -> Endings:
    return make_nonpast_endings(iu, II, iiuu + AA, UU + ALIF, iiuu + NA)


JUSS_ENDINGS_II = _make_juss_endings_ii_uu(I, II)
JUSS_ENDINGS_UU = _make_juss_endings_ii_uu(U, UU)


def imperative_endings_from_jussive(endings: Endings) -> Endings:
    """Extract the second-person jussive endings to get the imperative endings (by person name)."""
    return [endings[pn_index(pn)] for pn in IMP_PERSON_NUMBERS]


IMP_ENDINGS = imperative_endings_from_jussive(JUSS_ENDINGS)
IMP_ENDINGS_ALT_A = imperative_endings_from_jussive(JUSS_ENDINGS_ALT_A)
IMP_ENDINGS_ALT_I = imperative_endings_from_jussive(JUSS_ENDINGS_ALT_I)
IMP_ENDINGS_AA = imperative_endings_from_jussive(JUSS_ENDINGS_AA)
IMP_ENDINGS_II = imperative_endings_from_jussive(JUSS_ENDINGS_II)
IMP_ENDINGS_UU = imperative_endings_from_jussive(JUSS_ENDINGS_UU)


def with_person(endings: Endings, pn: str, ending: AbForms) -> Endings:
    """A 13-entry table with one entry replaced, named by person (ar-verb.lua set_2fs, 1521-1538)."""
    out = list(endings)
    out[pn_index(pn)] = ending
    return out


def with_imp_person(endings: Endings, pn: str, ending: AbForms) -> Endings:
    out = list(endings)
    out[imp_index(pn)] = ending
    return out
