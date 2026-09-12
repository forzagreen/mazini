"""Form I: sound/assimilated, the حَيِيَ/عَيِيَ paradigm, final-weak, hollow and geminate.

Port of ar-verb.lua 941-990 (irregular-root predicates) and 1755-2161.
"""

from __future__ import annotations

from ..base import Base, VowelSpec, insert_ap2_pp2, insert_form_or_forms, skip_slot
from ..chars import _I, AA, AAMAQ, AAN, ALIF, HAMZA, II, IN, MA, SH, SK, UU, A, I, N, U, W, Y, pn_index
from ..endings import (
    IMP_ENDINGS_AA,
    IND_ENDINGS_AA,
    JUSS_ENDINGS_AA,
    NONPAST_PREFIX_CONSONANTS,
    PAST_ENDINGS,
    SUB_ENDINGS_AA,
    make_nonpast_endings,
)  # fmt: skip
from ..errors import internal
from ..forms import AbForm, combine_form_and_footnotes, map_vowel, q, req, rget
from ..radicals import final_weak_uu_retains_rad3, geminate_degemination_vowel, hayy_radicals, is_waw_ya
from ..tense import (
    all_same,
    inflect_tense,
    inflect_tense_1,
    inflect_tense_imp,
    make_1stem_imperative,
    nonpast_1stem_conj,
    past_2stem_conj,
)  # fmt: skip
from .common import make_final_weak_verb, make_hollow_geminate_verb, make_sound_verb

#: The clitic note on the long imperative of أَمَرَ, as the module emits it (frame:preprocess is identity).
CLITIC_NOTE = "[used especially with a clitic such as {{m|ar|فَ}} or {{m|ar|وَ}}]"


# ---- radicals of the irregular verbs (ar-verb.lua 958-990)
def axadh_radicals(rad1: AbForm, rad2: AbForm, rad3: AbForm) -> bool:
    return req(rad1, HAMZA) and req(rad2, "خ") and req(rad3, "ذ")


def reduced_imperative_verb(rad1: AbForm, rad2: AbForm, rad3: AbForm) -> str | None:
    """أكل/أخذ: "shortonly"; أمر: "shortlong" (long imperatives after a clitic); else None."""
    if axadh_radicals(rad1, rad2, rad3):
        return "shortonly"
    if req(rad1, HAMZA) and req(rad2, "ك") and req(rad3, "ل"):
        return "shortonly"
    if req(rad1, HAMZA) and req(rad2, "م") and req(rad3, "ر"):
        return "shortlong"
    return None


def raa_radicals(rad1: AbForm, rad2: AbForm, rad3: AbForm) -> bool:
    return req(rad1, "ر") and req(rad2, HAMZA) and is_waw_ya(rad3)


def saal_radicals(rad1: AbForm, rad2: AbForm, rad3: AbForm) -> bool:
    return req(rad1, "س") and req(rad2, HAMZA) and req(rad3, "ل")


def kaan_radicals(rad1: AbForm, rad2: AbForm, rad3: AbForm) -> bool:
    return req(rad1, "ك") and req(rad2, W) and req(rad3, N)


def saal_hollow_radicals(rad1: AbForm, rad2: AbForm, rad3: AbForm) -> bool:
    return req(rad1, "س") and req(rad2, W) and req(rad3, "ل")


def _rads3(vs: VowelSpec) -> tuple[str, str, str, str, str]:
    assert vs.rad1 is not None and vs.rad2 is not None and vs.rad3 is not None
    return vs.rad1, vs.rad2, vs.rad3, vs.past, vs.nonpast


def form_i_imp_stem_through_rad1(base: Base, nonpast_vowel: AbForm, rad1: AbForm) -> AbForm:
    """The imperative stem up to and including rad1: hamzat wasl with the class vowel, rad1, sukūn."""

    def imp_vowel_of(vow: str) -> str:
        if vow in (A, I):
            return I
        if vow == U:
            return U
        if not skip_slot(base, "imp_2ms"):
            internal("Non-past vowel " + vow + " isn't a, i, or u, should have been caught earlier")
        return I  # passive-only; the imperative is never displayed

    imp_vowel = map_vowel(nonpast_vowel, imp_vowel_of)
    vowel_on_alif = map_vowel(imp_vowel, lambda vow: ALIF + vow)
    return q(vowel_on_alif, rad1, SK)


def make_form_i_sound_assimilated_verb(base: Base, vs: VowelSpec, assimilated: bool) -> None:
    """Form-I sound or assimilated verb."""
    rad1, rad2, rad3, past_vowel, nonpast_vowel = _rads3(vs)

    past_stem = q(rad1, A, rad2, past_vowel, rad3)
    nonpast_stem = q(rad2, nonpast_vowel, rad3) if assimilated else q(rad1, SK, rad2, nonpast_vowel, rad3)
    past_pass_stem = q(rad1, U, rad2, I, rad3)
    nonpast_pass_stem = q(rad1, SK, rad2, A, rad3)

    reducedimp = reduced_imperative_verb(rad1, rad2, rad3)
    if reducedimp:
        base.irregular = True
    imp_stem_suffix = q(rad2, nonpast_vowel, rad3)
    long_imp_stem_base = form_i_imp_stem_through_rad1(base, nonpast_vowel, rad1)
    imp_stem = q("" if (assimilated or reducedimp) else long_imp_stem_base, imp_stem_suffix)

    # A form-I mithal that keeps its wāw spells its imperative on a hamzat wasl (اِوْجَلْ); see #10
    if not assimilated and req(rad1, W):
        base.orth.keep_initial_w = True

    make_sound_verb(base, past_stem, past_pass_stem, nonpast_stem, nonpast_pass_stem, imp_stem, "a")

    if reducedimp == "shortlong":
        make_1stem_imperative(base, combine_form_and_footnotes(q(long_imp_stem_base, imp_stem_suffix), CLITIC_NOTE))

    # سَأَلَ: alternative jussive and imperative سَل
    if saal_radicals(rad1, rad2, rad3):
        base.irregular = True
        nonpast_1stem_conj(base, "juss", "a", "سَل")
        nonpast_1stem_conj(base, "juss_pass", "u", "سَل")
        make_1stem_imperative(base, "سَل")

    insert_form_or_forms(base, "ap1", q(rad1, AA, rad2, I, rad3))
    insert_ap2_pp2(base, q(rad1, A, rad2, II, rad3))
    insert_form_or_forms(base, "ap3", q(rad1, A, rad2, I, rad3))
    insert_form_or_forms(base, "apcd", q(HAMZA, A, rad1, SK, rad2, A, rad3))
    insert_form_or_forms(base, "apan", q(rad1, A, rad2, SK, rad3, AAN))
    insert_form_or_forms(base, "pp", q(MA, rad1, SK, rad2, UU, rad3))


def make_form_i_hayy_verb(base: Base, vs: VowelSpec) -> None:
    """The إدغام-contracting form-I final-weak verb: حَيَّ beside حَيِيَ, عَيَّ beside عَيِيَ."""
    base.irregular = True
    rad1, rad2, rad3, _, _ = _rads3(vs)

    past_c_stem = q(rad1, A, rad2, I, rad3)
    past_v_stem_long = past_c_stem
    past_v_stem_short = q(rad1, A, rad2, SH)
    past_v_stem_3mp = q(rad1, A, rad2)  # حَيُوا, not the geminated حَيُّوا
    past_pass_c_stem = q(rad1, U, rad2, I, rad3)
    past_pass_v_stem_long = past_pass_c_stem
    past_pass_v_stem_short = q(rad1, U, rad2, SH)
    past_pass_v_stem_3mp = q(rad1, U, rad2)

    nonpast_stem = q(rad1, SK, rad2)
    nonpast_pass_stem = nonpast_stem
    imp_stem = q(_I, nonpast_stem)

    past_2stem_conj(base, "past", [], past_c_stem)
    past_2stem_conj(base, "past_pass", [], past_pass_c_stem)
    variant = vs.variant or "both"
    if variant in ("short", "both"):
        past_2stem_conj(base, "past", past_v_stem_short, [])
        past_2stem_conj(base, "past_pass", past_pass_v_stem_short, [])

    def inflect_long_variant(tense: str, long_stem: AbForm, mp_stem: AbForm) -> None:
        inflect_tense_1(base, tense, "",
                        [long_stem, long_stem, long_stem, long_stem, mp_stem],
                        [PAST_ENDINGS[pn_index("3ms")], PAST_ENDINGS[pn_index("3fs")], PAST_ENDINGS[pn_index("3md")],
                         PAST_ENDINGS[pn_index("3fd")], PAST_ENDINGS[pn_index("3mp")]],
                        ["3ms", "3fs", "3md", "3fd", "3mp"])  # fmt: skip

    if variant in ("long", "both"):
        inflect_long_variant("past", past_v_stem_long, past_v_stem_3mp)
        inflect_long_variant("past_pass", past_pass_v_stem_long, past_pass_v_stem_3mp)

    nonpast_1stem_conj(base, "ind", "a", nonpast_stem, IND_ENDINGS_AA)
    nonpast_1stem_conj(base, "sub", "a", nonpast_stem, SUB_ENDINGS_AA)
    nonpast_1stem_conj(base, "juss", "a", nonpast_stem, JUSS_ENDINGS_AA)
    nonpast_1stem_conj(base, "ind_pass", "u", nonpast_pass_stem, IND_ENDINGS_AA)
    nonpast_1stem_conj(base, "sub_pass", "u", nonpast_pass_stem, SUB_ENDINGS_AA)
    nonpast_1stem_conj(base, "juss_pass", "u", nonpast_pass_stem, JUSS_ENDINGS_AA)
    inflect_tense_imp(base, all_same(imp_stem), IMP_ENDINGS_AA)

    insert_form_or_forms(base, "ap1", q(rad1, AA, rad2, IN))
    insert_ap2_pp2(base, q(rad1, A, rad2, II, SH))
    insert_form_or_forms(base, "ap3", q(rad1, A, rad2, IN))
    insert_form_or_forms(base, "apcd", q(HAMZA, A, rad1, SK, rad2, AAMAQ))
    insert_form_or_forms(base, "apan", q(rad1, A, rad2, SK, rad3, AAN))
    insert_form_or_forms(base, "pp", q(MA, rad1, SK, rad2, II if req(rad3, Y) else UU, SH))


def make_form_i_final_weak_verb(base: Base, vs: VowelSpec, assimilated: bool) -> None:
    """Form-I final-weak or assimilated+final-weak verb."""
    rad1, rad2, rad3, past_vowel, nonpast_vowel = _rads3(vs)

    if hayy_radicals(rad1, rad2, rad3, "I"):
        make_form_i_hayy_verb(base, vs)
        return

    past_stem = q(rad1, A, rad2)
    past_pass_stem = q(rad1, U, rad2)
    nonpast_stem: AbForm
    nonpast_pass_stem: AbForm
    imp_stem: AbForm
    if raa_radicals(rad1, rad2, rad3):
        base.irregular = True
        nonpast_stem = rad1
        nonpast_pass_stem = rad1
        imp_stem = rad1
    else:
        nonpast_pass_stem = q(rad1, SK, rad2)
        if assimilated:
            nonpast_stem = rad2
            imp_stem = rad2
        else:
            nonpast_stem = nonpast_pass_stem
            imp_stem = q(form_i_imp_stem_through_rad1(base, nonpast_vowel, rad1), rad2)

    if not assimilated and req(rad1, W):
        base.orth.keep_initial_w = True

    if req(rad3, Y) and req(past_vowel, A):
        past_ending_vowel = "ay"
    elif req(rad3, W) and req(past_vowel, A):
        past_ending_vowel = "aw"
    elif req(past_vowel, I):
        past_ending_vowel = "ī"
    else:
        past_ending_vowel = "ū"
    nonpast_ending_vowel = "ā" if req(nonpast_vowel, A) else "ī" if req(nonpast_vowel, I) else "ū"
    make_final_weak_verb(
        base,
        past_stem,
        past_pass_stem,
        nonpast_stem,
        nonpast_pass_stem,
        imp_stem,
        past_ending_vowel,
        nonpast_ending_vowel,
        "a",
        final_weak_uu_retains_rad3(past_ending_vowel, nonpast_ending_vowel),
    )

    insert_form_or_forms(base, "ap1", q(rad1, AA, rad2, IN))
    insert_ap2_pp2(base, q(rad1, A, rad2, II, SH))
    insert_form_or_forms(base, "ap3", q(rad1, A, rad2, IN))
    insert_form_or_forms(base, "apcd", q(HAMZA, A, rad1, SK, rad2, AAMAQ))
    insert_form_or_forms(base, "apan", q(rad1, A, rad2, SK, rad3, AAN))
    insert_form_or_forms(base, "pp", q(MA, rad1, SK, rad2, II if req(rad3, Y) else UU, SH))


def make_form_i_hollow_verb(base: Base, vs: VowelSpec) -> None:
    """Form-I hollow verb."""
    rad1, rad2, rad3, past_vowel_in, nonpast_vowel = _rads3(vs)
    # i~i and u~u were mapped to a~i and a~u by infer_radicals(); undo that to get the actual past vowel.
    past_vowel: AbForm = past_vowel_in
    if req(past_vowel, A):
        past_vowel = map_vowel(past_vowel, lambda _vow: I if req(nonpast_vowel, A) else rget(nonpast_vowel))
    lengthened_nonpast = map_vowel(nonpast_vowel, lambda vow: UU if vow == U else II if vow == I else AA)

    past_v_stem = q(rad1, AA, rad3)
    past_c_stem = q(rad1, past_vowel, rad3)
    nonpast_v_stem = q(rad1, lengthened_nonpast, rad3)
    nonpast_c_stem = q(rad1, nonpast_vowel, rad3)
    # 'ufīla always; the contracted passive past takes whichever of i/u the active past_c_stem isn't.
    past_pass_v_stem = q(rad1, II, rad3)
    past_pass_c_stem = q(rad1, map_vowel(past_vowel, lambda vow: U if vow == I else I), rad3)
    nonpast_pass_v_stem = q(rad1, AA, rad3)
    nonpast_pass_c_stem = q(rad1, A, rad3)
    imp_v_stem = nonpast_v_stem
    imp_c_stem = nonpast_c_stem

    make_hollow_geminate_verb(
        base,
        False,
        past_v_stem,
        past_c_stem,
        past_pass_v_stem,
        past_pass_c_stem,
        nonpast_v_stem,
        nonpast_c_stem,
        nonpast_pass_v_stem,
        nonpast_pass_c_stem,
        imp_v_stem,
        imp_c_stem,
        "a",
    )

    if kaan_radicals(rad1, rad2, rad3):
        endings = make_nonpast_endings(U, [], [], [], [])
        inflect_tense(base, "juss", NONPAST_PREFIX_CONSONANTS, q(A, rad1), endings)  # type: ignore[arg-type]
        base.irregular = True

    # سالَ يَسالُ keeps سَأَلْتُ's fatḥa in its contracted past (سَلْتَ); README finding #19
    if saal_hollow_radicals(rad1, rad2, rad3) and req(nonpast_vowel, A):
        base.irregular = True
        past_2stem_conj(base, "past", past_v_stem, q(rad1, A, rad3))

    insert_form_or_forms(base, "ap1", q(rad1, AA, HAMZA, IN) if req(rad3, HAMZA) else q(rad1, AA, HAMZA, I, rad3))
    insert_ap2_pp2(base, q(rad1, A, Y, SH, I, rad3))
    insert_form_or_forms(base, "ap3", q(rad1, A, Y, I, rad3))
    insert_form_or_forms(base, "apcd", q(HAMZA, A, rad1, SK, rad2, A, rad3))
    insert_form_or_forms(base, "apan", q(rad1, A, rad2, SK, rad3, AAN))
    insert_form_or_forms(base, "pp", q(MA, rad1, II if req(rad2, Y) else UU, rad3))


def make_form_i_geminate_verb(base: Base, vs: VowelSpec) -> None:
    """Form-I geminate verb."""
    rad1, rad2, rad3, past_vowel, nonpast_vowel = _rads3(vs)

    past_v_stem = q(rad1, A, rad2, SH)
    past_c_stem = q(rad1, A, rad2, geminate_degemination_vowel(rad1, rad2, rad3, past_vowel, nonpast_vowel), rad2)
    nonpast_v_stem = q(rad1, nonpast_vowel, rad2, SH)
    nonpast_c_stem = q(rad1, SK, rad2, nonpast_vowel, rad2)
    past_pass_v_stem = q(rad1, U, rad2, SH)
    past_pass_c_stem = q(rad1, U, rad2, I, rad2)
    nonpast_pass_v_stem = q(rad1, A, rad2, SH)
    nonpast_pass_c_stem = q(rad1, SK, rad2, A, rad2)
    imp_v_stem = q(rad1, nonpast_vowel, rad2, SH)
    imp_c_stem = q(form_i_imp_stem_through_rad1(base, nonpast_vowel, rad1), rad2, nonpast_vowel, rad2)

    make_hollow_geminate_verb(
        base,
        True,
        past_v_stem,
        past_c_stem,
        past_pass_v_stem,
        past_pass_c_stem,
        nonpast_v_stem,
        nonpast_c_stem,
        nonpast_pass_v_stem,
        nonpast_pass_c_stem,
        imp_v_stem,
        imp_c_stem,
        "a",
    )

    insert_form_or_forms(base, "ap1", q(rad1, AA, rad2, SH))
    insert_ap2_pp2(base, q(rad1, A, rad2, II, rad2))
    insert_form_or_forms(base, "ap3", q(rad1, A, rad2, SH))
    insert_form_or_forms(base, "apcd", q(HAMZA, A, rad1, A, rad2, SH))
    insert_form_or_forms(base, "apan", q(rad1, A, rad2, SH, AAN))
    insert_form_or_forms(base, "pp", q(MA, rad1, SK, rad2, UU, rad2))
