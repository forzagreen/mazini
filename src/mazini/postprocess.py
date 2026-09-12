"""The orthography passes run over every finished form.

Port of ar-verb.lua 669-675 (apply_nfc_shadda), 2872-2896 (postprocess_subs), 2938-3120
(postprocess_term), 3149-3175 (add_naql_idgham_forms) and 3177-3202 (postprocess_forms). The
BORDER/placeholder scheme is kept literally: the rule order and the parked sequences are the algorithm.
"""

from __future__ import annotations

import re

from .base import Base, Orth
from .chars import (
    AIU,
    ALIF,
    AMAD,
    AMAQ,
    BORDER,
    DIACRITIC_ANY_BUT_SH,
    HAMZA,
    HAMZA_ON_ALIF,
    HAMZA_ON_W,
    HAMZA_PH,
    HAMZA_UNDER_ALIF,
    II,
    KEEP_HAMZA_PH,
    KEEP_W_PH,
    NO_MADDA_PH,
    SH,
    SK,
    UU,
    WAW_SEAT_PH,
    A,
    I,
    U,
    W,
    Y,
)  # fmt: skip
from .forms import Form, FormTable, insert_form
from .hamza import process_hamza

_NFC_SHADDA_RE = re.compile(SH + "(" + DIACRITIC_ANY_BUT_SH + ")")


def apply_nfc_shadda(word: str) -> str:
    """apply_nfc_shadda: šadda + vowel → vowel + šadda, the order NFC (and MediaWiki) stores."""
    return _NFC_SHADDA_RE.sub(r"\1" + SH, word)


_POSTPROCESS_SUBS: list[tuple[re.Pattern[str] | str, str]] = [
    # reorder short-vowel + šadda -> šadda + short-vowel for easier processing
    (re.compile("(" + AIU + ")" + SH), SH + r"\1"),
    # same letter separated by sukūn should instead use šadda (kun-nā)
    (re.compile("(.)" + SK + r"\1"), r"\1" + SH),
    # assimilated verbs: iw, iy -> ī; uw, uy -> ū
    (I + W + SK, II),
    (I + Y + SK, II),
    (U + W + SK, UU),
    (U + Y + SK, UU),
    # final -yā uses tall alif not alif maqṣūra
    (re.compile("(" + Y + SH + "?" + A + ")" + AMAQ), r"\1" + ALIF),
    # hamza assimilation: initial hamza + short vowel + hamza + sukūn -> hamza + long vowel
    (HAMZA + A + HAMZA + SK, HAMZA + A + ALIF),
    (HAMZA + I + HAMZA + SK, HAMZA + I + Y),
    (HAMZA + U + HAMZA + SK, HAMZA + U + W),
]


def _apply_subs(t: str) -> str:
    for frm, to in _POSTPROCESS_SUBS:
        t = t.replace(frm, to) if isinstance(frm, str) else frm.sub(to, t)
    return t


_PARK_W_FROM = BORDER + ALIF + I + W + SK
_PARK_W_TO = BORDER + ALIF + I + KEEP_W_PH + SK
_PARK_HAMZA_FROM = BORDER + HAMZA + A + HAMZA + SK
_PARK_HAMZA_TO = BORDER + HAMZA + A + KEEP_HAMZA_PH + SK
_HAMZA_A_ALIF_END = HAMZA + A + ALIF + BORDER
_HAMZA_A_AMAQ_END = HAMZA + A + AMAQ + BORDER
_W_HAMZA_U_W = W + HAMZA + U + W
_SEAT_FINAL_RE = re.compile(SK + HAMZA + "(" + AIU + ")" + BORDER)
_NO_MADDA_FROM = ALIF + HAMZA + A + ALIF + BORDER
_NO_MADDA_TO = ALIF + NO_MADDA_PH + A + ALIF + BORDER
_MADDA_AFTER_LONG_RE = re.compile("([" + AMAD + ALIF + W + Y + "])" + HAMZA + A + ALIF)
_ALIF_KASRA = HAMZA_ON_ALIF + I
_ALIF_KASRA_BELOW = HAMZA_UNDER_ALIF + I


def _reduce(term: str, orth: Orth, park_w: bool) -> str:
    """Phase 1: the reductions, with the parked exemptions held out across them."""
    t = BORDER + term + BORDER
    # #10: a word-initial hamzat wasl + wāw + sukūn is a retained-wāw mithal imperative (اِوْنَ)
    if park_w:
        t = t.replace(_PARK_W_FROM, _PARK_W_TO)
    # #14: hamza-initial form VIII spells its 1s مضارع analytically (أَأْتَمِنُ)
    if orth.analytic_hamza:
        t = t.replace(_PARK_HAMZA_FROM, _PARK_HAMZA_TO)
    t = _apply_subs(t)
    # #12, the past half: the ā of a wāw-rad3 past 3ms after a hamza rad2 is written as alif maqṣūra
    if orth.hamza_rad2_final_weak:
        t = t.replace(_HAMZA_A_ALIF_END, _HAMZA_A_AMAQ_END)
    t = t.replace(KEEP_W_PH, W)
    t = t.replace(KEEP_HAMZA_PH, HAMZA)
    return t.replace(BORDER, "")


def _seat_final(m: re.Match[str]) -> str:
    vowel = m.group(1)
    return SK + (HAMZA_ON_W if vowel == U else HAMZA_ON_ALIF) + vowel + BORDER


def _seat(t: str, orth: Orth) -> list[str]:
    """Phase 2: hamza seats. Returns the list of spellings for one reduced term."""
    if HAMZA not in t:
        return [t]
    # #17: keep the wāw seat after a long ū beside the two spellings process_hamza returns
    waw_seat: str | None = None
    if _W_HAMZA_U_W in t:
        parked = t.replace(_W_HAMZA_U_W, W + WAW_SEAT_PH + U + W)
        waw_seat = process_hamza(parked.replace(HAMZA, HAMZA_PH))[0].replace(WAW_SEAT_PH, HAMZA_ON_W)
    out = process_hamza(t.replace(HAMZA, HAMZA_PH))
    if waw_seat is not None:
        out.append(waw_seat)
    # #12, the imperative/jussive half: a stranded radical hamza after a sukūn takes its own vowel's seat
    if orth.hamza_rad2_final_weak:
        for i, v in enumerate(out):
            out[i] = _SEAT_FINAL_RE.sub(_seat_final, BORDER + v + BORDER).replace(BORDER, "")
    # #15: a hamza on the line after a long vowel, with fatḥa + alif after it, is written as a madda,
    # except word-finally directly after an alif
    for i, v in enumerate(out):
        v = BORDER + v + BORDER
        v = v.replace(_NO_MADDA_FROM, _NO_MADDA_TO)
        v = _MADDA_AFTER_LONG_RE.sub(r"\1" + AMAD, v)
        v = v.replace(NO_MADDA_PH, HAMZA)
        out[i] = v.replace(BORDER, "")
    # #18: a hamza seated on an alif and carrying a bare kasra is written below the alif
    for i, v in enumerate(out):
        out[i] = v.replace(_ALIF_KASRA, _ALIF_KASRA_BELOW)
    return out


def postprocess_term(term: str, orth: Orth | None) -> str | list[str]:
    """postprocess_term: the finished spelling(s) of one form."""
    if term == "?":
        return "?"
    orth = orth if orth is not None else Orth()
    out = _seat(_reduce(term, orth, orth.keep_initial_w), orth)
    # #16: a retained-wāw mithal imperative is printed both ways (اِوْنَ and اِينَ), so carry both
    if orth.keep_initial_w:
        for reduced in _seat(_reduce(term, orth, False), orth):
            if reduced not in out:
                out.append(reduced)
    return out[0] if len(out) == 1 else out


# #13: نقل الحركة + إدغام in a لفيف مقرون verb outside form I (أَحْيَيَا -> أَحَيَّا).
_NAQL_RE = re.compile("(.)" + SK + Y + "(" + AIU + ")" + Y + "(" + AIU + ")")
_NAQL_TO = r"\1\2" + Y + SK + Y + r"\3"


def add_naql_idgham_forms(base: Base) -> None:
    if base.verb_form == "I":
        return
    additions: list[tuple[str, Form]] = []
    for slot, forms in base.forms.items():
        for form in forms:
            if _NAQL_RE.search(form.form):
                additions.append((slot, Form(_NAQL_RE.sub(_NAQL_TO, form.form), form.footnotes)))
    for slot, form in additions:
        insert_form(base.forms, slot, form)


def postprocess_forms(base: Base) -> None:
    """postprocess_forms: run postprocess_term over every slot, deduplicating the spellings it returns."""
    for slot in list(base.forms):
        forms = base.forms[slot]
        converted = [postprocess_term(f.form, base.orth) for f in forms]
        if not any(c != forms[i].form for i, c in enumerate(converted)):
            continue
        dedup: FormTable = {}
        for i, form in enumerate(forms):
            terms = converted[i]
            for term in terms if isinstance(terms, list) else [terms]:
                insert_form(dedup, "temp", Form(term, form.footnotes))
        base.forms[slot] = dedup["temp"]
