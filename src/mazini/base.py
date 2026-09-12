"""The per-verb state the builders write into, and the slot helpers around it.

Port of ar-verb.lua 681-817 and of the fields parse_indicator_spec/detect_indicator_spec set
(3352-3362, 3650-3932).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from .forms import (
    AbForm,
    AbForms,
    Form,
    FormTable,
    add_forms,
    add_multiple_forms,
    insert_form,
    insert_forms,
    to_general_list,
)

PassiveType = str  # "pass" | "ipass" | "nopass" | "onlypass" | "onlypass-impers"
Weakness = str  # "sound" | "assimilated" | "final-weak" | "assimilated+final-weak" | "hollow" | "geminate"


@dataclass(slots=True)
class VowelSpec:
    #: Past and non-past stem vowels as diacritics (A/I/U), or "-" for the augmented forms.
    past: str
    nonpast: str
    rad1: str | None = None
    rad2: str | None = None
    rad3: str | None = None
    rad4: str | None = None
    weakness: str | None = None
    #: Form VIII: the infixed tāʾ joined to the first radical (form_viii_join_ta).
    form_viii_assim: str | None = None
    variant: str | None = None


@dataclass(slots=True)
class Orth:
    keep_initial_w: bool = False
    analytic_hamza: bool = False
    hamza_rad2_final_weak: bool = False

    def keys(self) -> list[str]:
        return [k for k in ("analytic_hamza", "hamza_rad2_final_weak", "keep_initial_w") if getattr(self, k)]


@dataclass(slots=True)
class Base:
    lemma: str  # "ك_ت_ب"
    verb_form: str
    conj_vowels: list[VowelSpec]
    passive: str | None = None
    passive_uncertain: bool = False
    passive_defaulted: bool = False
    reduced: bool = False
    altgem: bool = False
    nopast: bool = False
    noimp: bool = False
    no_nonpast: bool = False
    nocat: bool = False
    variant: str | None = None
    quadlit: bool = False
    irregular: bool = False
    forms: FormTable = field(default_factory=dict)
    slot_uncertain: dict[str, bool] = field(default_factory=dict)
    orth: Orth = field(default_factory=Orth)
    grouped_conj_vowels: list[tuple[list[str], list[str]]] = field(default_factory=list)


def new_base(
    lemma: str, verb_form: str, conj_vowels: list[VowelSpec], *, passive: bool = False, reduced: bool = False
) -> Base:
    return Base(
        lemma=lemma,
        verb_form=verb_form,
        conj_vowels=conj_vowels,
        passive="pass" if passive else None,
        reduced=bool(reduced),
        quadlit=verb_form.endswith("q"),
    )


def skip_slot(base: Base, slot: str) -> bool:
    """skip_slot: whether the verb's passive type and flags leave this slot empty."""
    pas = "_pass" in slot
    if base.passive == "nopass" and (slot == "pp" or pas):
        return True
    if base.passive == "onlypass" and slot != "pp" and slot != "vn" and not pas:
        return True
    if base.passive == "ipass" and pas and "3ms" not in slot:
        return True
    if base.passive == "onlypass-impers" and slot != "pp" and slot != "vn" and (not pas or (pas and "3ms" not in slot)):
        return True
    if base.nopast and slot.startswith("past_"):
        return True
    if base.noimp and slot.startswith("imp_"):
        return True
    if base.no_nonpast and (slot.startswith("ind_") or slot.startswith("sub_") or slot.startswith("juss")):
        return True
    return False


def _concat(stem: str, ending: str) -> str:
    return stem + ending


def add3(base: Base, slot: str, prefixes: AbForms, stems: AbForms, endings: AbForms) -> None:
    """add3: prefix + stem + ending into `slot`."""
    if skip_slot(base, slot):
        return
    if isinstance(prefixes, str):
        p = prefixes
        add_forms(base.forms, slot, stems, endings, lambda stem, ending: p + stem + ending)
    else:
        add_multiple_forms(base.forms, slot, [prefixes, stems, endings], _concat)


def insert_form_or_forms(base: Base, slot: str, form_or_forms: AbForms, uncertain: bool = False) -> None:
    """insert_form_or_forms: an abbreviated form list into `slot`, unless the slot is skipped."""
    if skip_slot(base, slot):
        return
    if isinstance(form_or_forms, str):
        insert_form(base.forms, slot, Form(form_or_forms, None, uncertain))
        return
    lst = to_general_list(form_or_forms)
    if uncertain:
        lst = [replace(f, uncertain=True) for f in lst]
    insert_forms(base.forms, slot, lst)


def insert_ap2_pp2(base: Base, string_or_form: AbForm) -> None:
    """Insert into both ap2 and pp2 (form objects are immutable here, so no copy is needed)."""
    insert_form_or_forms(base, "ap2", string_or_form)
    insert_form_or_forms(base, "pp2", string_or_form)


def stem_or_empty(default_stem: AbForms | None) -> AbForms:
    """override_stem_if_needed without user overrides: the default stem, or [] when there is none."""
    return [] if default_stem is None else default_stem
