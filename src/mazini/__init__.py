"""mazini: every form of an Arabic verb from its root and pattern.

A port of Arabic Wiktionary's Module:ar-verb (وحدة:ar-verb), root + وزن path.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .chars import IMP_PERSON_NUMBERS, PERSON_NUMBERS, POTENTIAL_LEMMA_SLOTS, SLOTS, UNSETTABLE_SLOTS
from .classify import classify_triliteral_verb
from .conjugations import conjugate_verb
from .detect import build_base, detect_indicator_spec
from .errors import MaziniError
from .forms import Form as _Form
from .loose import loose, norm
from .properties import (
    collect_forms,
    compute_morph_patterns,
    determine_slot_uncertainty,
    determine_verb_properties,
    get_verb_info,
)
from .radicals import normalize_root
from .wazn import WAZN_BY_NAME, WAZNS, Vowels, WaznInfo, parse_form_code

__all__ = [
    "IMP_PERSON_NUMBERS", "PERSON_NUMBERS", "POTENTIAL_LEMMA_SLOTS", "SLOTS", "UNSETTABLE_SLOTS", "WAZNS",
    "Conjugation", "Form", "MaziniError", "Vowels", "WaznInfo", "classify_triliteral_verb", "conjugate", "get_verb_type",
    "loose", "norm", "normalize_root",
]  # fmt: skip

__version__ = "0.1.0"


@dataclass(frozen=True, slots=True)
class Form:
    form: str
    footnotes: tuple[str, ...] = ()
    uncertain: bool = False


@dataclass(slots=True)
class Conjugation:
    #: Every slot the verb has, in table order; a slot the verb lacks is absent.
    slots: dict[str, list[Form]]
    #: All 119 slot names, in table order.
    slot_list: tuple[str, ...]
    #: The citation form: the first of POTENTIAL_LEMMA_SLOTS the verb has.
    lemma: list[Form]
    verb_form: str
    form_code: str
    #: The وزن name, or None for forms XIV and XV which have none.
    wazn: str | None
    radicals: list[str]
    root_display: str
    weakness: str
    quadriliteral: bool
    vowels: Vowels | None
    passive: str
    passive_uncertain: bool
    passive_defaulted: bool
    reduced: bool
    irregular: bool
    form_viii_assim: str | None
    orth: dict[str, bool]
    morph_patterns: list[str]
    verb_forms: list[str]
    has_active: bool
    has_passive: bool
    #: Slots whose value is the "?" placeholder (an unknown form-I مصدر or participle).
    uncertain_slots: list[str]
    #: «فعل ثلاثي مُجرَّد صحيح سالم»
    verb_type: str
    #: «صحيح سالم», «معتل أجوف واوي», …; None for quadriliteral roots.
    classification: str | None = None
    _extra: dict = field(default_factory=dict, repr=False)


def _resolve(wazn: str, vowels: Vowels | tuple[str, str] | None) -> tuple[str, Vowels | None, str, str | None]:
    info = WAZN_BY_NAME.get(wazn)
    if info:
        return info.verb_form, info.vowels, info.form_code, info.wazn
    parsed = parse_form_code(wazn)
    if parsed:
        by_code = next((w for w in WAZNS if w.form_code == wazn), None)
        return parsed[0], parsed[1], wazn, by_code.wazn if by_code else None
    if wazn == "I" and vowels is not None:
        v = vowels if isinstance(vowels, Vowels) else Vowels(*vowels)
        code = "I/%s~%s" % (v.past, v.nonpast)
        by_code = next((w for w in WAZNS if w.form_code == code), None)
        if by_code is None:
            raise MaziniError("unknown_wazn", "Unknown form-I vowels: " + code)
        return "I", by_code.vowels, code, by_code.wazn
    raise MaziniError("unknown_wazn", "Unknown morphological pattern (وزن صرفي): " + wazn)


def _output(f: _Form) -> Form:
    return Form(f.form, tuple(f.footnotes) if f.footnotes else (), bool(f.uncertain))


def conjugate(
    root: str,
    wazn: str,
    *,
    passive: bool = False,
    reduced: bool = False,
    vowels: Vowels | tuple[str, str] | None = None,
) -> Conjugation:
    """Conjugate a verb.

    `root` is three or four radicals ("كتب", "ك ت ب" or "ك_ت_ب"); `wazn` is a pattern name ("فعَل يفعُل",
    "استفعل") or a form code ("I/a~u", "X", "XIV"). `passive` is |مبني للمجهول= (a full personal passive),
    `reduced` is |مدغم= (the assimilated shape of the affix). `vowels` supplies the form-I stem vowels when
    `wazn` is the bare "I".
    """
    radicals = normalize_root(root)
    verb_form, vs_vowels, form_code, wazn_name = _resolve(wazn, vowels)
    base = build_base(radicals, verb_form, vs_vowels, passive=passive, reduced=reduced)
    detect_indicator_spec(base)
    conjugate_verb(base)

    forms = collect_forms(base)
    uncertain_slots = determine_slot_uncertainty(base, forms)
    has_active, has_passive = determine_verb_properties(forms)
    morph_patterns = compute_morph_patterns(base)
    root_display, verb_type, classification = get_verb_info(base, morph_patterns)

    slots = {slot: [_output(f) for f in forms[slot]] for slot in SLOTS if slot in forms}
    lemma: list[Form] = []
    for slot in POTENTIAL_LEMMA_SLOTS:
        if slot in slots:
            lemma = slots[slot]
            break
    vs = base.conj_vowels[0]
    assert vs.weakness is not None and base.passive is not None
    return Conjugation(
        slots=slots,
        slot_list=SLOTS,
        lemma=lemma,
        verb_form=verb_form,
        form_code=form_code,
        wazn=wazn_name,
        radicals=radicals,
        root_display=root_display,
        weakness=vs.weakness,
        quadriliteral=base.quadlit,
        vowels=vs_vowels,
        passive=base.passive,
        passive_uncertain=base.passive_uncertain,
        passive_defaulted=base.passive_defaulted,
        reduced=base.reduced,
        irregular=base.irregular,
        form_viii_assim=vs.form_viii_assim,
        orth={k: True for k in base.orth.keys()},
        morph_patterns=morph_patterns,
        verb_forms=[] if base.nocat else [verb_form],
        has_active=has_active,
        has_passive=has_passive,
        uncertain_slots=uncertain_slots,
        verb_type=verb_type,
        classification=classification,
    )


def get_verb_type(root: str, wazn: str, *, passive: bool = False, reduced: bool = False) -> str:
    """The «فعل ثلاثي مُجرَّد صحيح سالم» line, as Module:ar-verb's get_verb_type gives it."""
    return conjugate(root, wazn, passive=passive, reduced=reduced).verb_type
