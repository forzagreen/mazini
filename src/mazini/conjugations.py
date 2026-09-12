"""The dispatch table (verb form + weakness → builder) and conjugate_verb.

Port of ar-verb.lua 1844-2739 (the conjugations[...] entries) and 3298-3347 (conjugate_verb), plus the
ap1 → ap promotion of process_slot_overrides (3251-3264), the only part of it that runs without user overrides.
"""

from __future__ import annotations

from collections.abc import Callable

from .base import Base, VowelSpec, skip_slot
from .builders.augmented import (
    make_form_ii_v_sound_final_weak_verb,
    make_form_iii_vi_geminate_verb,
    make_form_iii_vi_sound_final_weak_verb,
    make_form_iiiq_sound_final_weak_verb,
    make_form_iq_iiq_sound_final_weak_verb,
    make_form_iv_geminate_verb,
    make_form_iv_hollow_verb,
    make_form_iv_sound_final_weak_verb,
    make_form_ivq_sound_verb,
    make_form_ix_final_weak_verb,
    make_form_ix_sound_verb,
    make_form_vii_geminate_verb,
    make_form_vii_hollow_verb,
    make_form_vii_sound_final_weak_verb,
    make_form_viii_geminate_verb,
    make_form_viii_hollow_verb,
    make_form_viii_sound_final_weak_verb,
    make_form_x_geminate_verb,
    make_form_x_hollow_verb,
    make_form_x_sound_final_weak_verb,
    make_form_xi_sound_verb,
    make_form_xii_sound_final_weak_verb,
    make_form_xiii_sound_final_weak_verb,
    make_form_xiv_xv_sound_final_weak_verb,
)  # fmt: skip
from .builders.form1 import (
    make_form_i_final_weak_verb,
    make_form_i_geminate_verb,
    make_form_i_hollow_verb,
    make_form_i_sound_assimilated_verb,
)  # fmt: skip
from .chars import HAMZA_ANY_RE, A
from .errors import MaziniError
from .forms import req
from .postprocess import add_naql_idgham_forms, postprocess_forms

Builder = Callable[[Base, VowelSpec], None]

CONJUGATIONS: dict[str, Builder] = {
    "I-sound": lambda b, v: make_form_i_sound_assimilated_verb(b, v, False),
    "I-assimilated": lambda b, v: make_form_i_sound_assimilated_verb(b, v, True),
    "I-final-weak": lambda b, v: make_form_i_final_weak_verb(b, v, False),
    "I-assimilated+final-weak": lambda b, v: make_form_i_final_weak_verb(b, v, True),
    "I-hollow": make_form_i_hollow_verb,
    "I-geminate": make_form_i_geminate_verb,
    "II-sound": make_form_ii_v_sound_final_weak_verb,
    "II-final-weak": make_form_ii_v_sound_final_weak_verb,
    "III-sound": make_form_iii_vi_sound_final_weak_verb,
    "III-final-weak": make_form_iii_vi_sound_final_weak_verb,
    "III-geminate": make_form_iii_vi_geminate_verb,
    "IV-sound": make_form_iv_sound_final_weak_verb,
    "IV-final-weak": make_form_iv_sound_final_weak_verb,
    "IV-hollow": make_form_iv_hollow_verb,
    "IV-geminate": make_form_iv_geminate_verb,
    "V-sound": make_form_ii_v_sound_final_weak_verb,
    "V-final-weak": make_form_ii_v_sound_final_weak_verb,
    "VI-sound": make_form_iii_vi_sound_final_weak_verb,
    "VI-final-weak": make_form_iii_vi_sound_final_weak_verb,
    "VI-geminate": make_form_iii_vi_geminate_verb,
    "VII-sound": make_form_vii_sound_final_weak_verb,
    "VII-final-weak": make_form_vii_sound_final_weak_verb,
    "VII-hollow": make_form_vii_hollow_verb,
    "VII-geminate": make_form_vii_geminate_verb,
    "VIII-sound": make_form_viii_sound_final_weak_verb,
    "VIII-final-weak": make_form_viii_sound_final_weak_verb,
    "VIII-hollow": make_form_viii_hollow_verb,
    "VIII-geminate": make_form_viii_geminate_verb,
    "IX-sound": make_form_ix_sound_verb,
    "IX-final-weak": make_form_ix_final_weak_verb,
    "X-sound": make_form_x_sound_final_weak_verb,
    "X-final-weak": make_form_x_sound_final_weak_verb,
    "X-hollow": make_form_x_hollow_verb,
    "X-geminate": make_form_x_geminate_verb,
    "XI-sound": make_form_xi_sound_verb,
    "XII-sound": make_form_xii_sound_final_weak_verb,
    "XII-final-weak": make_form_xii_sound_final_weak_verb,
    "XIII-sound": make_form_xiii_sound_final_weak_verb,
    "XIII-final-weak": make_form_xiii_sound_final_weak_verb,
    "XIV-sound": make_form_xiv_xv_sound_final_weak_verb,
    "XIV-final-weak": make_form_xiv_xv_sound_final_weak_verb,
    "XV-sound": make_form_xiv_xv_sound_final_weak_verb,
    "Iq-sound": make_form_iq_iiq_sound_final_weak_verb,
    "Iq-final-weak": make_form_iq_iiq_sound_final_weak_verb,
    "IIq-sound": make_form_iq_iiq_sound_final_weak_verb,
    "IIq-final-weak": make_form_iq_iiq_sound_final_weak_verb,
    "IIIq-sound": make_form_iiiq_sound_final_weak_verb,
    "IIIq-final-weak": make_form_iiiq_sound_final_weak_verb,
    "IVq-sound": make_form_ivq_sound_verb,
}


def conjugate_verb(base: Base) -> None:
    """conjugate_verb: build every slot of `base.forms`."""
    for vs in base.conj_vowels:
        conj_type = base.verb_form + "-" + str(vs.weakness)
        # #14: a hamza-initial form VIII spells its 1s مضارع analytically (أَأْتَمِنُ)
        if base.verb_form == "VIII" and vs.rad1 is not None and HAMZA_ANY_RE.search(vs.rad1):
            base.orth.analytic_hamza = True
        # #12: a final-weak verb whose rad2 is a hamza
        if "final-weak" in (vs.weakness or "") and vs.rad2 is not None and HAMZA_ANY_RE.search(vs.rad2):
            base.orth.hamza_rad2_final_weak = True
        builder = CONJUGATIONS.get(conj_type)
        if builder is None:
            raise MaziniError("unsupported_weakness", "Unknown conjugation type '" + conj_type + "'")
        builder(base, vs)
    # #13: before postprocess_forms(), which supplies the إدغام half of the alternation.
    add_naql_idgham_forms(base)
    postprocess_forms(base)
    _promote_ap1(base)


def _promote_ap1(base: Base) -> None:
    """For non-stative form-I verbs, fill the active participle from ap1."""
    if base.verb_form == "I" and "ap" not in base.forms and "ap1" in base.forms and not skip_slot(base, "ap"):
        if any(req(vs.past, A) for vs in base.conj_vowels):
            base.forms["ap"] = base.forms.pop("ap1")
