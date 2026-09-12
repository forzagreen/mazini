"""After conjugation: the slot table in table order, the "?" placeholders, has_active/has_passive, the
morph patterns and the verb-type phrase.

Port of iut's single-word copy (inflection utilities.lua 1190-1249), ar-verb.lua 3968-4034 and
get_verb_info (4425-4462).
"""

from __future__ import annotations

import re
from dataclasses import replace

from .base import Base, skip_slot
from .chars import SLOTS, SLOTS_THAT_MAY_BE_UNCERTAIN
from .classify import classify_triliteral_verb
from .forms import Form, FormTable
from .postprocess import apply_nfc_shadda
from .radicals import is_passive_only
from .wazn import WAZN_BY_NAME, form_code_to_wazn

_PERSONAL_RE = re.compile("[123]")


def collect_forms(base: Base) -> FormTable:
    """The top-level form table: every slot in table order, forms copied, šadda written after its vowel."""
    forms: FormTable = {}
    for slot in SLOTS:
        lst = base.forms.get(slot)
        if lst is None:
            continue
        forms[slot] = [replace(f, form=apply_nfc_shadda(f.form)) for f in lst]
    return forms


def determine_slot_uncertainty(base: Base, forms: FormTable) -> list[str]:
    """determine_slot_uncertainty_from_forms: an unknown form-I مصدر or participle shows as "?"."""
    for slot in SLOTS_THAT_MAY_BE_UNCERTAIN:
        if slot not in base.forms and not skip_slot(base, slot):
            base.slot_uncertain[slot] = True
    for slot in SLOTS_THAT_MAY_BE_UNCERTAIN:
        if slot not in forms and base.slot_uncertain.get(slot):
            forms[slot] = [Form("?")]
    return sorted(base.slot_uncertain)


def determine_verb_properties(forms: FormTable) -> tuple[bool, bool]:
    has_active = False
    has_passive = False
    for slot in forms:
        personal = bool(_PERSONAL_RE.search(slot))
        pas = "_pass" in slot
        if slot == "ap" or (personal and not pas):
            has_active = True
        if slot == "pp" or (personal and pas):
            has_passive = True
    return has_active, has_passive


def compute_morph_patterns(base: Base) -> list[str]:
    """compute_morph_patterns: the وزن (or أوزان) the verb was conjugated on."""
    patterns: list[str] = []
    if base.nocat:
        return patterns

    def add(p: str | None) -> None:
        if p and p not in patterns:
            patterns.append(p)

    add(form_code_to_wazn(base.verb_form))
    if base.verb_form == "I" and not is_passive_only(base.passive):
        for pasts, nonpasts in base.grouped_conj_vowels:
            for past in pasts:
                for nonpast in nonpasts:
                    add(form_code_to_wazn("I/%s~%s" % (past, nonpast)))
    return patterns


def get_verb_info(base: Base, morph_patterns: list[str]) -> tuple[str, str, str | None]:
    """get_verb_info: the root as spaced letters, the «فعل ثلاثي مُجرَّد صحيح سالم» phrase, the classification."""
    vs = base.conj_vowels[0] if base.conj_vowels else None
    rad1, rad2, rad3, rad4 = (vs.rad1, vs.rad2, vs.rad3, vs.rad4) if vs else (None, None, None, None)
    basic_deriv = (
        WAZN_BY_NAME[morph_patterns[0]].basic_deriv if morph_patterns and morph_patterns[0] in WAZN_BY_NAME else None
    )
    if not (rad1 and rad2 and rad3):
        return "", "فعل", None
    if rad4:
        verb_type = "فعل رباعي"
        if basic_deriv:
            verb_type += " " + basic_deriv
        return " ".join((rad1, rad2, rad3, rad4)), verb_type, None
    verb_type = "فعل ثلاثي"
    classification = classify_triliteral_verb(rad1, rad2, rad3)
    if basic_deriv:
        verb_type += " " + basic_deriv
        if basic_deriv == "مُجرَّد":
            verb_type += " " + classification
    return " ".join((rad1, rad2, rad3)), verb_type, classification
