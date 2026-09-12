"""Forms II–XV and Iq–IVq. Port of ar-verb.lua 2166-2739."""

from __future__ import annotations

from ..base import Base, VowelSpec, insert_form_or_forms
from ..chars import _I, _U, AA, AAH, AH, HAMZA, II, IN, MU, SH, SK, TA, TU, UU, A, I, M, N, S, T, U, W, Y
from ..endings import PAST_ENDINGS_AY_12_PERSON_ONLY
from ..errors import MaziniError
from ..forms import AbForm, q, req, rget
from ..radicals import hayy_radicals
from ..tense import all_same, inflect_tense
from .common import (
    high_form_verbal_noun,
    is_final_weak,
    make_augmented_geminate_verb,
    make_augmented_hollow_verb,
    make_augmented_sound_final_weak_verb,
    make_high5_form_sound_final_weak_verb,
    make_high_form_sound_final_weak_verb,
)  # fmt: skip
from .form1 import axadh_radicals, raa_radicals


def _rads3(vs: VowelSpec) -> tuple[str, str, str]:
    assert vs.rad1 is not None and vs.rad2 is not None and vs.rad3 is not None
    return vs.rad1, vs.rad2, vs.rad3


def _rads4(vs: VowelSpec) -> tuple[str, str, str, str]:
    assert vs.rad1 is not None and vs.rad2 is not None and vs.rad3 is not None and vs.rad4 is not None
    return vs.rad1, vs.rad2, vs.rad3, vs.rad4


def _form_ii_iii_v_vi_ta_tu_prefix(base: Base, rad1: str) -> tuple[AbForm, AbForm, AbForm]:
    """The ta-/tu- prefixes of forms II/III/V/VI; reduced forms V/VI double rad1 across a sukūn instead."""
    vform = base.verb_form
    if vform in ("V", "VI"):
        if base.reduced:
            return q(_I, rad1, SK), q(rad1, SK), q(_U, rad1, SK)
        return TA, TA, TU
    return "", "", ""


def make_form_ii_v_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    final_weak = is_final_weak(base, vs)
    vform = base.verb_form
    ta_past, ta_nonpast, tu_past = _form_ii_iii_v_vi_ta_tu_prefix(base, rad1)
    if vform == "V":
        vn = q(ta_past, rad1, A, rad2, SH, IN if final_weak else q(U, rad3))
    else:
        vn = q(TA, rad1, SK, rad2, II, AH if final_weak else rad3)
    past_stem_base = q(ta_past, rad1, A, rad2, SH)
    nonpast_stem_base = q(ta_nonpast, rad1, A, rad2, SH)
    past_pass_stem_base = q(tu_past, rad1, U, rad2, SH)
    make_augmented_sound_final_weak_verb(base, vs, past_stem_base, nonpast_stem_base, past_pass_stem_base, vn)


def _make_form_iii_alt_vn(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    final_weak = is_final_weak(base, vs)
    insert_form_or_forms(base, "vn2", q(rad1, I, rad2, AA, HAMZA if final_weak else rad3))


def make_form_iii_vi_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    final_weak = is_final_weak(base, vs)
    vform = base.verb_form
    ta_past, ta_nonpast, tu_past = _form_ii_iii_v_vi_ta_tu_prefix(base, rad1)
    if vform == "VI":
        vn = q(ta_past, rad1, AA, rad2, IN if final_weak else q(U, rad3))
    else:
        vn = q(MU, rad1, AA, rad2, AAH if final_weak else q(A, rad3, AH))
    past_stem_base = q(ta_past, rad1, AA, rad2)
    nonpast_stem_base = q(ta_nonpast, rad1, AA, rad2)
    past_pass_stem_base = q(tu_past, rad1, UU, rad2)
    make_augmented_sound_final_weak_verb(base, vs, past_stem_base, nonpast_stem_base, past_pass_stem_base, vn)
    if vform == "III":
        _make_form_iii_alt_vn(base, vs)


def make_form_iii_vi_geminate_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, _ = _rads3(vs)
    vform = base.verb_form
    ta_past, ta_nonpast, tu_past = _form_ii_iii_v_vi_ta_tu_prefix(base, rad1)
    vn = q(ta_past, rad1, AA, rad2, SH) if vform == "VI" else q(MU, rad1, AA, rad2, SH, AH)
    past_stem_base = q(ta_past, rad1, AA)
    nonpast_stem_base = q(ta_nonpast, rad1, AA)
    past_pass_stem_base = q(tu_past, rad1, UU)
    variant = vs.variant or "short"
    if variant in ("short", "both"):
        make_augmented_geminate_verb(base, vs, past_stem_base, nonpast_stem_base, past_pass_stem_base, vn)
    # Also the uncompressed parts; duplicates are removed on insertion.
    if variant in ("long", "both"):
        make_form_iii_vi_sound_final_weak_verb(base, vs)
    elif vform == "III":
        _make_form_iii_alt_vn(base, vs)


def make_form_iv_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    final_weak = is_final_weak(base, vs)
    is_raa = raa_radicals(rad1, rad2, rad3)
    stem_core: AbForm
    if is_raa:
        base.irregular = True
        stem_core = rad1
    else:
        stem_core = q(rad1, SK, rad2)
    vn = q(HAMZA, I, stem_core, AA, HAMZA, AH) if is_raa else q(HAMZA, I, stem_core, AA, HAMZA if final_weak else rad3)
    make_augmented_sound_final_weak_verb(base, vs, q(HAMZA, A, stem_core), stem_core, q(HAMZA, U, stem_core), vn)


def make_form_iv_hollow_verb(base: Base, vs: VowelSpec) -> None:
    rad1, _, rad3 = _rads3(vs)
    vn = q(HAMZA, I, rad1, AA, rad3, AH)
    make_augmented_hollow_verb(base, vs, q(HAMZA, A, rad1), rad1, q(HAMZA, U, rad1), vn)


def make_form_iv_geminate_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, _ = _rads3(vs)
    vn = q(HAMZA, I, rad1, SK, rad2, AA, rad2)
    make_augmented_geminate_verb(base, vs, q(HAMZA, A, rad1), rad1, q(HAMZA, U, rad1), vn)


def _form_vii_nrad1(base: Base, rad1: str) -> AbForm:
    if base.reduced:
        if not req(rad1, M):
            raise MaziniError(
                "reduced_not_applicable",
                "Internal error: Form VII first radical "
                + rget(rad1)
                + " is not م but .reduced specified; should have been caught earlier",
            )
        return M + SH
    return q("نْ", rad1)


def make_form_vii_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    make_high_form_sound_final_weak_verb(base, vs, _form_vii_nrad1(base, rad1), rad2, rad3)


def make_form_vii_hollow_verb(base: Base, vs: VowelSpec) -> None:
    rad1, _, rad3 = _rads3(vs)
    nrad1 = _form_vii_nrad1(base, rad1)
    vn = high_form_verbal_noun(nrad1, Y, rad3)
    make_augmented_hollow_verb(base, vs, q(_I, nrad1), nrad1, q(_U, nrad1), vn)


def make_form_vii_geminate_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, _ = _rads3(vs)
    nrad1 = _form_vii_nrad1(base, rad1)
    vn = high_form_verbal_noun(nrad1, rad2, rad2)
    nonpast_stem_base = q(nrad1, A)
    make_augmented_geminate_verb(base, vs, q(_I, nonpast_stem_base), nonpast_stem_base, q(_U, nrad1, U), vn)


def _form_viii_verbal_noun(base: Base, vs: VowelSpec, rad2: AbForm, rad3: AbForm) -> list[AbForm]:
    final_weak = is_final_weak(base, vs)
    assert vs.form_viii_assim is not None
    return [high_form_verbal_noun(vs.form_viii_assim, rad2, HAMZA if final_weak else rad3)]


def make_form_viii_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    if axadh_radicals(rad1, rad2, rad3):
        base.irregular = True  # اِتَّخَذَ
    assert vs.form_viii_assim is not None
    make_high_form_sound_final_weak_verb(base, vs, vs.form_viii_assim, rad2, rad3)


def make_form_viii_hollow_verb(base: Base, vs: VowelSpec) -> None:
    _, _, rad3 = _rads3(vs)
    vn = _form_viii_verbal_noun(base, vs, Y, rad3)
    assert vs.form_viii_assim is not None
    nonpast_stem_base = vs.form_viii_assim
    make_augmented_hollow_verb(base, vs, q(_I, nonpast_stem_base), nonpast_stem_base, q(_U, nonpast_stem_base), vn)


def make_form_viii_geminate_verb(base: Base, vs: VowelSpec) -> None:
    _, rad2, _ = _rads3(vs)
    vn = _form_viii_verbal_noun(base, vs, rad2, rad2)
    assert vs.form_viii_assim is not None
    nonpast_stem_base = q(vs.form_viii_assim, A)
    make_augmented_geminate_verb(
        base, vs, q(_I, nonpast_stem_base), nonpast_stem_base, q(_U, vs.form_viii_assim, U), vn
    )


def make_form_ix_sound_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    vn = q(_I, rad1, SK, rad2, I, rad3, AA, rad3)
    nonpast_stem_base = q(rad1, SK, rad2, A)
    make_augmented_geminate_verb(base, vs, q(_I, nonpast_stem_base), nonpast_stem_base, q(_U, rad1, SK, rad2, U), vn)


def make_form_ix_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    make_high_form_sound_final_weak_verb(base, vs, q(rad1, SK, rad2), rad3, rad3)


def make_form_x_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    is_hayy = hayy_radicals(rad1, rad2, rad3)
    variant = vs.variant or "both"
    if not is_hayy or variant in ("long", "both"):
        make_high5_form_sound_final_weak_verb(base, vs, S, T, rad1, rad2, rad3)
    if is_hayy and variant in ("short", "both"):
        base.irregular = True
        make_high_form_sound_final_weak_verb(base, vs, S + SK + T, rad1, rad3)


def make_form_x_hollow_verb(base: Base, vs: VowelSpec) -> None:
    rad1, _, rad3 = _rads3(vs)
    vn = q("اِسْ" if base.reduced else "اِسْتِ", rad1, AA, rad3, AH)
    past_stem_base = q("اِسْ" if base.reduced else "اِسْتَ", rad1)
    nonpast_stem_base = q("سْ" if base.reduced else "سْتَ", rad1)
    past_pass_stem_base = q("اُسْ" if base.reduced else "اُسْتُ", rad1)
    make_augmented_hollow_verb(base, vs, past_stem_base, nonpast_stem_base, past_pass_stem_base, vn)


def make_form_x_geminate_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, _ = _rads3(vs)
    vn = q("اِسْتِ", rad1, SK, rad2, AA, rad2)
    past_stem_base = q("اِسْتَ", rad1)
    nonpast_stem_base = q("سْتَ", rad1)
    past_pass_stem_base = q("اُسْتُ", rad1)
    if base.altgem:
        inflect_tense(base, "past", "", all_same(q(past_stem_base, A, rad2, SH)), PAST_ENDINGS_AY_12_PERSON_ONLY)
    make_augmented_geminate_verb(
        base, vs, past_stem_base, nonpast_stem_base, past_pass_stem_base, vn, "[uncommon]" if base.altgem else None
    )


def make_form_xi_sound_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    vn = q(_I, rad1, SK, rad2, II, rad3, AA, rad3)
    nonpast_stem_base = q(rad1, SK, rad2, AA)
    make_augmented_geminate_verb(base, vs, q(_I, nonpast_stem_base), nonpast_stem_base, q(_U, rad1, SK, rad2, UU), vn)


def make_form_xii_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    make_high5_form_sound_final_weak_verb(base, vs, rad1, rad2, W, rad2, rad3)


def make_form_xiii_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    make_high5_form_sound_final_weak_verb(base, vs, rad1, rad2, W, W, rad3)


def make_form_xiv_xv_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3 = _rads3(vs)
    lastrad = Y if base.verb_form == "XV" else rad3
    make_high5_form_sound_final_weak_verb(base, vs, rad1, rad2, N, rad3, lastrad)


def make_form_iq_iiq_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3, rad4 = _rads4(vs)
    final_weak = is_final_weak(base, vs)
    vform = base.verb_form
    if vform == "IIq":
        vn = q(TA, rad1, A, rad2, SK, rad3, IN if final_weak else q(U, rad4))
    else:
        vn = q(rad1, A, rad2, SK, rad3, AAH if final_weak else q(A, rad4, AH))
    ta_pref = TA if vform == "IIq" else ""
    tu_pref = TU if vform == "IIq" else ""
    past_stem_base = q(ta_pref, rad1, A, rad2, SK, rad3)
    nonpast_stem_base = past_stem_base
    past_pass_stem_base = q(tu_pref, rad1, U, rad2, SK, rad3)
    make_augmented_sound_final_weak_verb(base, vs, past_stem_base, nonpast_stem_base, past_pass_stem_base, vn)


def _form_iiiq_n_augment(base: Base, rad3: str) -> AbForm:
    """The نون of اِفْعَنْلَلَ, or the إدغام that replaces it when |مدغم= and ل1 is weak."""
    if not base.reduced:
        return N
    if not (req(rad3, W) or req(rad3, Y)):
        raise MaziniError(
            "reduced_not_applicable",
            "Form IIIq .reduced assimilates the نون into ل1, which must be و or ي, but saw " + rget(rad3),
        )
    return rad3


def make_form_iiiq_sound_final_weak_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3, rad4 = _rads4(vs)
    make_high5_form_sound_final_weak_verb(base, vs, rad1, rad2, _form_iiiq_n_augment(base, rad3), rad3, rad4)


def make_form_ivq_sound_verb(base: Base, vs: VowelSpec) -> None:
    rad1, rad2, rad3, rad4 = _rads4(vs)
    vn = q(_I, rad1, SK, rad2, I, rad3, SK, rad4, AA, rad4)
    past_stem_base = q(_I, rad1, SK, rad2, A, rad3)
    nonpast_stem_base = q(rad1, SK, rad2, A, rad3)
    past_pass_stem_base = q(_U, rad1, SK, rad2, U, rad3)
    make_augmented_geminate_verb(base, vs, past_stem_base, nonpast_stem_base, past_pass_stem_base, vn)
