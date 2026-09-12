"""Hamza seating: port of module/ar-utilities.lua 183-298 (reorder_shadda, hamza_subs, process_hamza)."""

from __future__ import annotations

import re
from collections.abc import Callable

from .chars import (
    ALIF,
    AMAD,
    AN,
    DIACRITIC_ANY_BUT_SH,
    HAMZA,
    HAMZA_ON_ALIF,
    HAMZA_ON_W,
    HAMZA_ON_Y,
    HAMZA_PH,
    HAMZA_UNDER_ALIF,
    SH,
    SK,
    A,
    I,
    U,
    W,
    Y,
)  # fmt: skip

_AIU_C = "[َُِ]"
# A diacritic that may sit on a consonant: optional šadda then one non-šadda mark (DIACRITIC in ar-utilities).
_DIA_OPT = SH + "?" + DIACRITIC_ANY_BUT_SH + "?"

_REORDER_RE = re.compile("(" + DIACRITIC_ANY_BUT_SH + ")" + SH)


def reorder_shadda(text: str) -> str:
    """reorder_shadda: short-vowel + šadda → šadda + short-vowel (undoes NFC ordering)."""
    return _REORDER_RE.sub(SH + r"\1", text)


def _seat_from_vowel(v: str) -> str:
    return HAMZA_ON_Y if v == I else HAMZA_ON_W if v == U else HAMZA_ON_ALIF


def _final(m: re.Match[str]) -> str:
    v, diacrit = m.group(1), m.group(3)
    return v + _seat_from_vowel(v) + diacrit


def _medial_after_long(m: re.Match[str]) -> str:
    prec, shad, v2 = m.group(1), m.group(3), m.group(4)
    if v2 == I or v2 == Y:
        ham = HAMZA_ON_Y
    elif v2 == U or v2 == W:
        ham = HAMZA_ON_W
    elif Y in prec:
        ham = HAMZA_ON_Y
    else:
        ham = HAMZA
    return prec + ham + shad + v2


def _medial(m: re.Match[str]) -> str:
    v1, shad, v2 = m.group(1), m.group(3), m.group(4)
    if v1 == I or v2 == I or v2 == Y:
        ham = HAMZA_ON_Y
    elif v1 == U or v2 == U or v2 == W:
        ham = HAMZA_ON_W
    elif v2 == AN + ALIF:  # avoid two alifs in a row before the indefinite accusative (جُزْءًا)
        ham = HAMZA
    else:
        ham = HAMZA_ON_ALIF
    return v1 + ham + shad + v2


_HAMZA_SUBS: list[tuple[re.Pattern[str], str | Callable[[re.Match[str]], str]]] = [
    # ---- initial hamza: seat according to the following vowel
    (re.compile("^" + HAMZA_PH + "([" + I + Y + "])"), HAMZA_UNDER_ALIF + r"\1"),
    (re.compile(" " + HAMZA_PH + "([" + I + Y + "])"), " " + HAMZA_UNDER_ALIF + r"\1"),
    (re.compile("^" + HAMZA_PH), HAMZA_ON_ALIF),  # if no vowel, assume a
    (re.compile(" " + HAMZA_PH), " " + HAMZA_ON_ALIF),
    # ---- final hamza: may be followed by a short vowel or tanwīn; use the previous short vowel for the seat
    (re.compile("(" + _AIU_C + ")(" + HAMZA_PH + ")(" + _DIA_OPT + r")\Z"), _final),
    (re.compile("(" + _AIU_C + ")(" + HAMZA_PH + ")(" + _DIA_OPT + " )"), _final),
    # else hamza is on the line
    (re.compile(HAMZA_PH + "(" + _DIA_OPT + r")\Z"), HAMZA + r"\1"),
    # ---- medial hamza: if a long vowel or diphthong precedes, ignore it
    (re.compile("([" + AMAD + ALIF + W + Y + "]" + SK + "?)(" + HAMZA_PH + ")(" + SH + "?)([^ ])"), _medial_after_long),
    # otherwise the seat relates to the vowels on one or both sides
    (re.compile("([^ ])(" + HAMZA_PH + ")(" + SH + "?)(" + AN + "?[^ ])"), _medial),
    # ---- alif madda
    (re.compile(HAMZA_ON_ALIF + A + "?" + ALIF), AMAD),
    # ---- catch any remaining hamzas
    (re.compile(HAMZA_PH), HAMZA),
]

_W_UU = W + "ؤُو"
_Y_UU = Y + "ؤُو"
_ALIF_UU = ALIF + "ؤُو"


def process_hamza(term: str) -> list[str]:
    """process_hamza: seat every placeholder hamza; returns the list of acceptable spellings."""
    for pat, repl in _HAMZA_SUBS:
        term = pat.sub(repl, term)
    # hamza-on-wāw + wāw is problematic and leads to alternatives (see ar-utilities.lua 275-297)
    if _W_UU in term:
        return [term.replace(_W_UU, W + "ئُو"), term.replace(_W_UU, W + "ءُو")]
    if _Y_UU in term:
        return [term.replace(_Y_UU, Y + "ئُو"), term]
    if _ALIF_UU in term:
        return [term.replace(_ALIF_UU, ALIF + "ئُو"), term]
    return [term]
