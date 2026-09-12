"""Whole-verb builders shared by several forms. Port of ar-verb.lua 1448-1777 and 2371-2395."""

from __future__ import annotations

from ..base import Base, VowelSpec, insert_form_or_forms, stem_or_empty
from ..chars import _I, _U, AA, AMAQ, AN, HAMZA, II, IN, MU, SH, SK, UU, A, I
from ..endings import (
    IMP_ENDINGS_AA,
    IMP_ENDINGS_II,
    IMP_ENDINGS_UU,
    IND_ENDINGS_AA,
    IND_ENDINGS_II,
    IND_ENDINGS_UU,
    JUSS_ENDINGS_AA,
    JUSS_ENDINGS_II,
    JUSS_ENDINGS_UU,
    PAST_ENDINGS_AW,
    PAST_ENDINGS_AY,
    PAST_ENDINGS_II,
    PAST_ENDINGS_UU,
    SUB_ENDINGS_AA,
    SUB_ENDINGS_II,
    SUB_ENDINGS_UU,
    Endings,
    with_imp_person,
    with_person,
)  # fmt: skip
from ..errors import internal
from ..forms import AbForm, AbForms, q
from ..radicals import prefix_vowel_from_vform, vform_nonpast_a_vowel
from ..tense import (
    all_same,
    inflect_tense,
    inflect_tense_imp,
    jussive_gem_conj,
    make_1stem_imperative,
    make_2stem_imperative,
    make_gem_imperative,
    nonpast_1stem_conj,
    nonpast_2stem_conj,
    past_1stem_conj,
    past_2stem_conj,
)  # fmt: skip


def is_final_weak(base: Base, vs: VowelSpec) -> bool:
    """Form XV (اِفْعَنْلَى) is final-weak by shape, whatever the root's third radical."""
    return vs.weakness == "final-weak" or base.verb_form == "XV"


def make_sound_verb(
    base: Base,
    past_stem: AbForms | None,
    past_pass_stem: AbForms | None,
    nonpast_stem: AbForms | None,
    nonpast_pass_stem: AbForms | None,
    imp_stem: AbForms | None,
    prefix_vowel: str,
) -> None:
    """Finite parts of a sound (or assimilated) verb from five stems plus the active non-past prefix vowel."""
    past_1stem_conj(base, "past", past_stem)
    past_1stem_conj(base, "past_pass", past_pass_stem)
    nonpast_1stem_conj(base, "ind", prefix_vowel, nonpast_stem)
    nonpast_1stem_conj(base, "sub", prefix_vowel, nonpast_stem)
    nonpast_1stem_conj(base, "juss", prefix_vowel, nonpast_stem)
    nonpast_1stem_conj(base, "ind_pass", "u", nonpast_pass_stem)
    nonpast_1stem_conj(base, "sub_pass", "u", nonpast_pass_stem)
    nonpast_1stem_conj(base, "juss_pass", "u", nonpast_pass_stem)
    make_1stem_imperative(base, imp_stem)


def _past_final_weak_endings_from_vowel(vowel: str) -> Endings:
    if vowel == "ay":
        return PAST_ENDINGS_AY
    if vowel == "aw":
        return PAST_ENDINGS_AW
    if vowel == "ī":
        return PAST_ENDINGS_II
    if vowel == "ū":
        return PAST_ENDINGS_UU
    internal("Unrecognized past final-weak vowel spec '" + vowel + "'")


def _nonpast_final_weak_endings_from_vowel(vowel: str) -> tuple[Endings, Endings, Endings, Endings]:
    if vowel == "ā":
        return IND_ENDINGS_AA, SUB_ENDINGS_AA, JUSS_ENDINGS_AA, IMP_ENDINGS_AA
    if vowel == "ī":
        return IND_ENDINGS_II, SUB_ENDINGS_II, JUSS_ENDINGS_II, IMP_ENDINGS_II
    if vowel == "ū":
        return IND_ENDINGS_UU, SUB_ENDINGS_UU, JUSS_ENDINGS_UU, IMP_ENDINGS_UU
    internal("Unrecognized non-past final-weak vowel spec '" + vowel + "'")


def make_final_weak_verb(
    base: Base,
    past_stem: AbForm,
    past_pass_stem: AbForm,
    nonpast_stem: AbForm,
    nonpast_pass_stem: AbForm,
    imp_stem: AbForm,
    past_ending_vowel: str,
    nonpast_ending_vowel: str,
    prefix_vowel: str,
    retain_rad3_2fs: bool = False,
) -> None:
    """Finite parts of a final-weak verb. `retain_rad3_2fs` keeps rad3 as a consonant before the 2fs -ī."""
    past_endings = _past_final_weak_endings_from_vowel(past_ending_vowel)
    past_pass_endings = _past_final_weak_endings_from_vowel("ī")
    ind_endings, sub_endings, juss_endings, imp_endings = _nonpast_final_weak_endings_from_vowel(nonpast_ending_vowel)
    ind_pass_endings, sub_pass_endings, juss_pass_endings, _ = _nonpast_final_weak_endings_from_vowel("ā")

    if retain_rad3_2fs:
        # rad3 surfaces as a consonant carrying the class's own ḍamma, then the regular -ī
        ind_endings = with_person(ind_endings, "2fs", UU + II + "نَ")
        sub_endings = with_person(sub_endings, "2fs", UU + II)
        juss_endings = with_person(juss_endings, "2fs", UU + II)
        imp_endings = with_imp_person(imp_endings, "2fs", UU + II)

    inflect_tense(base, "past", "", all_same(stem_or_empty(past_stem)), past_endings)
    inflect_tense(base, "past_pass", "", all_same(stem_or_empty(past_pass_stem)), past_pass_endings)
    nonpast_1stem_conj(base, "ind", prefix_vowel, nonpast_stem, ind_endings)
    nonpast_1stem_conj(base, "sub", prefix_vowel, nonpast_stem, sub_endings)
    nonpast_1stem_conj(base, "juss", prefix_vowel, nonpast_stem, juss_endings)
    nonpast_1stem_conj(base, "ind_pass", "u", nonpast_pass_stem, ind_pass_endings)
    nonpast_1stem_conj(base, "sub_pass", "u", nonpast_pass_stem, sub_pass_endings)
    nonpast_1stem_conj(base, "juss_pass", "u", nonpast_pass_stem, juss_pass_endings)
    inflect_tense_imp(base, all_same(stem_or_empty(imp_stem)), imp_endings)


def make_augmented_final_weak_verb(
    base: Base,
    past_stem: AbForm,
    past_pass_stem: AbForm,
    nonpast_stem: AbForm,
    nonpast_pass_stem: AbForm,
    imp_stem: AbForm,
    prefix_vowel: str,
    form56: bool,
) -> None:
    """An augmented (form II+) final-weak verb: past in -ay, non-past in -ā (forms V/VI) or -ī."""
    make_final_weak_verb(
        base,
        past_stem,
        past_pass_stem,
        nonpast_stem,
        nonpast_pass_stem,
        imp_stem,
        "ay",
        "ā" if form56 else "ī",
        prefix_vowel,
    )


def make_augmented_sound_final_weak_verb(
    base: Base,
    vs: VowelSpec,
    past_stem_base: AbForm,
    nonpast_stem_base: AbForm,
    past_pass_stem_base: AbForm,
    vn: AbForms,
) -> None:
    """An augmented sound or final-weak verb from its three stem bases and its مصدر."""
    insert_form_or_forms(base, "vn", vn)

    lastrad = vs.rad4 if base.quadlit else vs.rad3
    assert lastrad is not None
    final_weak = is_final_weak(base, vs)
    prefix_vowel = prefix_vowel_from_vform(base.verb_form)
    form56 = vform_nonpast_a_vowel(base.verb_form)
    a_base_suffix: AbForm = "" if final_weak else q(A, lastrad)
    i_base_suffix: AbForm = "" if final_weak else q(I, lastrad)

    past_stem = q(past_stem_base, a_base_suffix)
    # Forms V and VI have /a/ as the last stem vowel of the finite non-past but /i/ in the active participle.
    nonpast_stem = q(nonpast_stem_base, a_base_suffix if form56 else i_base_suffix)
    ap_stem = q(nonpast_stem_base, i_base_suffix)
    past_pass_stem = q(past_pass_stem_base, i_base_suffix)
    nonpast_pass_stem = q(nonpast_stem_base, a_base_suffix)
    imp_stem = q(past_stem_base, a_base_suffix if form56 else i_base_suffix)

    if final_weak:
        make_augmented_final_weak_verb(
            base, past_stem, past_pass_stem, nonpast_stem, nonpast_pass_stem, imp_stem, prefix_vowel, form56
        )
    else:
        make_sound_verb(base, past_stem, past_pass_stem, nonpast_stem, nonpast_pass_stem, imp_stem, prefix_vowel)

    if final_weak:
        insert_form_or_forms(base, "ap", q(MU, ap_stem, IN))
        insert_form_or_forms(base, "pp", q(MU, nonpast_pass_stem, AN, AMAQ))
    else:
        insert_form_or_forms(base, "ap", q(MU, ap_stem))
        insert_form_or_forms(base, "pp", q(MU, nonpast_pass_stem))


def make_hollow_geminate_verb(
    base: Base,
    geminate: bool,
    past_v_stem: AbForms | None,
    past_c_stem: AbForms | None,
    past_pass_v_stem: AbForms | None,
    past_pass_c_stem: AbForms | None,
    nonpast_v_stem: AbForms | None,
    nonpast_c_stem: AbForms | None,
    nonpast_pass_v_stem: AbForms | None,
    nonpast_pass_c_stem: AbForms | None,
    imp_v_stem: AbForms | None,
    imp_c_stem: AbForms | None,
    prefix_vowel: str,
    altgem_note: str | None = None,
) -> None:
    """Finite parts of a hollow or geminate verb from ten stems."""
    past_2stem_conj(base, "past", past_v_stem, past_c_stem, altgem_note)
    past_2stem_conj(base, "past_pass", past_pass_v_stem, past_pass_c_stem)
    nonpast_2stem_conj(base, "ind", prefix_vowel, nonpast_v_stem, nonpast_c_stem)
    nonpast_2stem_conj(base, "sub", prefix_vowel, nonpast_v_stem, nonpast_c_stem)
    nonpast_2stem_conj(base, "ind_pass", "u", nonpast_pass_v_stem, nonpast_pass_c_stem)
    nonpast_2stem_conj(base, "sub_pass", "u", nonpast_pass_v_stem, nonpast_pass_c_stem)
    if geminate:
        jussive_gem_conj(base, "juss", prefix_vowel, nonpast_v_stem, nonpast_c_stem)
        jussive_gem_conj(base, "juss_pass", "u", nonpast_pass_v_stem, nonpast_pass_c_stem)
        make_gem_imperative(base, imp_v_stem, imp_c_stem)
    else:
        nonpast_2stem_conj(base, "juss", prefix_vowel, nonpast_v_stem, nonpast_c_stem)
        nonpast_2stem_conj(base, "juss_pass", "u", nonpast_pass_v_stem, nonpast_pass_c_stem)
        make_2stem_imperative(base, imp_v_stem, imp_c_stem)


def make_augmented_hollow_verb(
    base: Base,
    vs: VowelSpec,
    past_stem_base: AbForm,
    nonpast_stem_base: AbForm,
    past_pass_stem_base: AbForm,
    vn: AbForms,
) -> None:
    """An augmented hollow verb from its stem bases and مصدر."""
    insert_form_or_forms(base, "vn", vn)
    lastrad = vs.rad4 if base.quadlit else vs.rad3
    assert lastrad is not None
    form410 = base.verb_form in ("IV", "X")
    prefix_vowel = prefix_vowel_from_vform(base.verb_form)

    a_base_suffix_v = q(AA, lastrad)  # 'af-āl-a, inf-āl-a
    a_base_suffix_c = q(A, lastrad)  # 'af-al-tu, inf-al-tu
    i_base_suffix_v = q(II, lastrad)  # 'uf-īl-a, unf-īl-a
    i_base_suffix_c = q(I, lastrad)  # 'uf-il-tu, unf-il-tu

    past_v_stem = q(past_stem_base, a_base_suffix_v)
    past_c_stem = q(past_stem_base, a_base_suffix_c)
    nonpast_v_stem = q(nonpast_stem_base, i_base_suffix_v if form410 else a_base_suffix_v)
    nonpast_c_stem = q(nonpast_stem_base, i_base_suffix_c if form410 else a_base_suffix_c)
    past_pass_v_stem = q(past_pass_stem_base, i_base_suffix_v)
    past_pass_c_stem = q(past_pass_stem_base, i_base_suffix_c)
    nonpast_pass_v_stem = q(nonpast_stem_base, a_base_suffix_v)
    nonpast_pass_c_stem = q(nonpast_stem_base, a_base_suffix_c)
    imp_v_stem = q(past_stem_base, i_base_suffix_v if form410 else a_base_suffix_v)
    imp_c_stem = q(past_stem_base, i_base_suffix_c if form410 else a_base_suffix_c)

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
        prefix_vowel,
    )

    insert_form_or_forms(base, "ap", q(MU, nonpast_v_stem))
    insert_form_or_forms(base, "pp", q(MU, nonpast_pass_v_stem))


def make_augmented_geminate_verb(
    base: Base,
    vs: VowelSpec,
    past_stem_base: AbForm,
    nonpast_stem_base: AbForm,
    past_pass_stem_base: AbForm,
    vn: AbForms,
    altgem_note: str | None = None,
) -> None:
    """An augmented geminate verb from its stem bases and مصدر (+ the form-X altgem footnote)."""
    insert_form_or_forms(base, "vn", vn)
    vform = base.verb_form
    lastrad = vs.rad4 if base.quadlit else vs.rad3
    assert lastrad is not None
    prefix_vowel = prefix_vowel_from_vform(vform)

    if vform in ("IV", "X", "IVq"):
        a_base_suffix_v = q(A, lastrad, SH)  # 'af-all
        a_base_suffix_c = q(SK, lastrad, A, lastrad)  # 'af-lal
        i_base_suffix_v = q(I, lastrad, SH)  # yuf-ill
        i_base_suffix_c = q(SK, lastrad, I, lastrad)  # yuf-lil
    else:
        a_base_suffix_v = q(lastrad, SH)  # fā-ll, infa-ll
        a_base_suffix_c = q(lastrad, A, lastrad)  # fā-lal, infa-lal
        i_base_suffix_v = q(lastrad, SH)  # yufā-ll, yanfa-ll
        i_base_suffix_c = q(lastrad, I, lastrad)  # yufā-lil, yanfa-lil
    a_vowel = vform_nonpast_a_vowel(vform)
    past_v_stem = q(past_stem_base, a_base_suffix_v)
    past_c_stem = q(past_stem_base, a_base_suffix_c)
    nonpast_v_stem = q(nonpast_stem_base, a_base_suffix_v if a_vowel else i_base_suffix_v)
    nonpast_c_stem = q(nonpast_stem_base, a_base_suffix_c if a_vowel else i_base_suffix_c)
    past_pass_v_stem = q(past_pass_stem_base, i_base_suffix_v)
    past_pass_c_stem = q(past_pass_stem_base, i_base_suffix_c)
    nonpast_pass_v_stem = q(nonpast_stem_base, a_base_suffix_v)
    nonpast_pass_c_stem = q(nonpast_stem_base, a_base_suffix_c)
    imp_v_stem = q(past_stem_base, a_base_suffix_v if a_vowel else i_base_suffix_v)
    imp_c_stem = q(past_stem_base, a_base_suffix_c if a_vowel else i_base_suffix_c)

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
        prefix_vowel,
        altgem_note,
    )

    insert_form_or_forms(base, "ap", q(MU, nonpast_v_stem))
    insert_form_or_forms(base, "pp", q(MU, nonpast_pass_v_stem))


def high_form_verbal_noun(rad12: AbForm, rad34: AbForm, rad5: AbForm) -> AbForm:
    """A مصدر of the shape shared by forms VII and above: اِفْعِلَال."""
    return q(_I, rad12, I, rad34, AA, rad5)


def make_high_form_sound_final_weak_verb(base: Base, vs: VowelSpec, rad12: AbForm, rad34: AbForm, rad5: AbForm) -> None:
    """A sound or final-weak verb of any high-numbered form: two consonant clusters and a final consonant."""
    final_weak = is_final_weak(base, vs)
    vn = high_form_verbal_noun(rad12, rad34, HAMZA if final_weak else rad5)
    nonpast_stem_base = q(rad12, A, rad34)
    past_stem_base = q(_I, nonpast_stem_base)
    past_pass_stem_base = q(_U, rad12, "ُ", rad34)
    make_augmented_sound_final_weak_verb(base, vs, past_stem_base, nonpast_stem_base, past_pass_stem_base, vn)


def make_high5_form_sound_final_weak_verb(
    base: Base, vs: VowelSpec, rad1: AbForm, rad2: AbForm, rad3: AbForm, rad4: AbForm, rad5: AbForm
) -> None:
    make_high_form_sound_final_weak_verb(base, vs, q(rad1, SK, rad2), q(rad3, SK, rad4), rad5)
