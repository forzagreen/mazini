"""Roots: normalisation, the lexical exception tables, weakness from radicals, and check_radicals.

Port of ar-verb.lua 561-660, 860-912, 2768-2868, 3564-3647 and 4740-4785.
"""

from __future__ import annotations

import re

from .chars import ALIF, AMAD, AMAQ, HAMZA, HAMZA_ON_ALIF, HAMZA_ON_W, HAMZA_ON_Y, HAMZA_UNDER_ALIF, SK, A, I, U, W, Y
from .errors import MaziniError
from .forms import AbForm, req

#: Lexical exceptions to the wāw-elision rule of form I, keyed root:past+nonpast (ar-verb.lua 561).
_FORM_I_W_ASSIMILATION: dict[str, bool] = {
    "وطء:ia": True,  # وَطِئَ ـَ / يَطَأُ / طَأْ: الدحداح، نموذج 155
    "وبء:aa": False,  # وَبَأَ ـَ / يَوْبَأُ / إِيبَأْ: الدحداح، نموذج 135
}


def _vowel_letter(v: AbForm | None) -> str:
    return "a" if req(v, A) else "i" if req(v, I) else "u" if req(v, U) else "?"


def form_i_w_assimilated(
    past_vowel: AbForm | None,
    nonpast_vowel: AbForm | None,
    rad1: str | None = None,
    rad2: str | None = None,
    rad3: str | None = None,
) -> bool:
    """True if a form-I verb whose first radical is wāw elides that wāw in the non-past (يَعِدُ, not يَوْعِدُ)."""
    if past_vowel is None or nonpast_vowel is None:
        return True
    if rad1 and rad2 and rad3:
        listed = _FORM_I_W_ASSIMILATION.get(
            rad1 + rad2 + rad3 + ":" + _vowel_letter(past_vowel) + _vowel_letter(nonpast_vowel)
        )
        if listed is not None:
            return listed
    return req(nonpast_vowel, I) or (req(nonpast_vowel, A) and req(past_vowel, A))


#: Geminate form-I roots whose degemination vowel follows the مضارع by إتباع (هَمُمْتَ).
_GEMINATE_ITBAA_ROOTS = frozenset({"همم", "عشش", "فكك", "شرر", "لبب"})


def geminate_degemination_vowel(rad1: str, rad2: str, rad3: str, past_vowel: AbForm, nonpast_vowel: AbForm) -> AbForm:
    if req(past_vowel, A) and req(nonpast_vowel, U) and (rad1 + rad2 + rad3) in _GEMINATE_ITBAA_ROOTS:
        return nonpast_vowel
    return past_vowel


def final_weak_uu_retains_rad3(past_ending_vowel: str, nonpast_ending_vowel: str) -> bool:
    """Form-I final-weak roots keep rad3 as a consonant before the 2fs -ī on the فعُل يفعُل measure (تَسْهُوِينَ)."""
    return past_ending_vowel == "ū" and nonpast_ending_vowel == "ū"


#: Roots the sources conjugate SOUND in a form whose rule would not, keyed form:root (ar-verb.lua 2768).
_SOUND_ROOTS = frozenset({
    "IV:خيل", "IV:غيل", "IV:حيج", "IV:حين", "IV:خيف", "IV:ريف", "IV:زين",
    "IV:ثوب", "IV:نيء", "VII:سيء", "VIII:عول", "VIII:زوج", "X:جوب", "III:علل", "III:فرر", "VI:عثث", "VI:غضض",
})  # fmt: skip

#: Hollow roots that keep the middle radical sound in one form-I vowel pattern, keyed root:vowels (هَيُؤَ, أَوِبَ).
_SOUND_FORM_I_ROOTS = frozenset({"هي" + HAMZA + ":uu", HAMZA + "وب:ia"})

#: Wāw-initial roots whose form VIII keeps the wāw instead of assimilating it (اِيتَشَى / يَوْتَشِي).
_FORM_VIII_UNASSIMILATED_W_ROOTS = frozenset({"وشي"})


def vform_supports_final_weak(vform: str) -> bool:
    return vform not in ("XI", "XV", "IVq")


def vform_supports_geminate(vform: str) -> bool:
    return vform in ("I", "III", "IV", "VI", "VII", "VIII", "X")


def vform_supports_hollow(vform: str) -> bool:
    return vform in ("I", "IV", "VII", "VIII", "X")


def vform_probably_impersonal_passive(vform: str, past_vowel: AbForm) -> bool:
    return (vform == "I" and req(past_vowel, I)) or vform in ("V", "VI", "X", "IIq")


def vform_probably_full_passive(vform: str) -> bool:
    return vform in ("II", "III", "IV", "Iq")


def vform_probably_no_passive(vform: str, past_vowel: AbForm) -> bool:
    return (vform == "I" and req(past_vowel, U)) or vform in (
        "VII",
        "IX",
        "XI",
        "XII",
        "XIII",
        "XIV",
        "XV",
        "IIIq",
        "IVq",
    )


def prefix_vowel_from_vform(vform: str) -> str:
    """Active forms II, III, IV, Iq take non-past prefixes in -u- instead of -a-."""
    return "u" if vform in ("II", "III", "IV", "Iq") else "a"


def vform_nonpast_a_vowel(vform: str) -> bool:
    """True if the active non-past takes a-vocalisation in its last syllable."""
    return vform in ("V", "VI", "XV", "IIq")


def is_passive_only(passive: str | None) -> bool:
    return passive in ("onlypass", "onlypass-impers")


def is_waw_ya(rad: AbForm | None) -> bool:
    return req(rad, W) or req(rad, Y)


def hayy_radicals(rad1: AbForm, rad2: AbForm, rad3: AbForm, vform: str | None = None) -> bool:
    """حَيِيَ / عَيِيَ: the form-I verbs whose past may contract by إدغام, and form X of حيي."""
    if not (req(rad2, Y) and is_waw_ya(rad3)):
        return False
    return req(rad1, "ح") or (vform == "I" and req(rad1, "ع"))


def weakness_from_radicals(
    form: str,
    rad1: str,
    rad2: str,
    rad3: str,
    rad4: str | None,
    past_vowel: AbForm | None,
    nonpast_vowel: AbForm | None,
) -> str:
    """weakness_from_radicals: the weakness class of a root under a form (the |جذر= + |وزن= path)."""
    quadlit = form.endswith("q")
    if not quadlit:
        if is_waw_ya(rad3) and rad1 == W and form == "I":
            return (
                "assimilated+final-weak"
                if form_i_w_assimilated(past_vowel, nonpast_vowel, rad1, rad2, rad3)
                else "final-weak"
            )
        if is_waw_ya(rad3) and vform_supports_final_weak(form):
            return "final-weak"
        if rad2 == rad3 and vform_supports_geminate(form):
            return "sound" if (form + ":" + rad1 + rad2 + rad3) in _SOUND_ROOTS else "geminate"
        if is_waw_ya(rad2) and vform_supports_hollow(form):
            if (form + ":" + rad1 + rad2 + rad3) in _SOUND_ROOTS:
                return "sound"
            if (
                form == "I"
                and past_vowel is not None
                and nonpast_vowel is not None
                and (rad1 + rad2 + rad3 + ":" + _vowel_letter(past_vowel) + _vowel_letter(nonpast_vowel))
                in _SOUND_FORM_I_ROOTS
            ):
                return "sound"
            return "hollow"
        if rad1 == W and form == "I":
            return "assimilated" if form_i_w_assimilated(past_vowel, nonpast_vowel, rad1, rad2, rad3) else "sound"
        return "sound"
    return "final-weak" if is_waw_ya(rad4) else "sound"


def form_viii_join_ta(rad: str, reduced: bool, root: str | None = None) -> str:
    """form_viii_join_ta: the infixed tāʾ joined to the first radical of a form VIII verb."""
    if rad == W and root is not None and root in _FORM_VIII_UNASSIMILATED_W_ROOTS:
        return W + SK + "ت"
    if rad in (W, Y, "ت"):
        return "تّ"
    if rad == HAMZA and reduced:
        return "تّ"
    special = {"د": "دّ", "ث": "ثّ", "ذ": "ذّ", "ز": "زْد", "ص": "صْط", "ض": "ضْط", "ط": "طّ", "ظ": "ظّ"}
    if rad in special:
        return special[rad]
    return rad + SK + "ت"


def check_radicals(form: str, weakness: str, rad1: str, rad2: str, rad3: str, rad4: str | None) -> None:
    """check_radicals: the radicals present are allowable for the weakness."""

    def fail(msg: str) -> None:
        raise MaziniError("invalid_radicals", msg)

    def hamza_check(index: int, rad: str | None) -> None:
        if rad in (HAMZA_ON_ALIF, HAMZA_UNDER_ALIF, HAMZA_ON_W, HAMZA_ON_Y):
            fail("Radical %d is %s but should be ء (hamza on the line)" % (index, rad))

    def check_waw_ya(index: int, rad: str) -> None:
        if not is_waw_ya(rad):
            fail("Radical %d is %s but should be و or ي" % (index, rad))

    def check_not_waw_ya(index: int, rad: str) -> None:
        if is_waw_ya(rad):
            fail("In a sound verb, radical %d should not be و or ي" % index)

    hamza_check(1, rad1)
    hamza_check(2, rad2)
    hamza_check(3, rad3)
    hamza_check(4, rad4)
    if weakness in ("assimilated", "assimilated+final-weak") and rad1 != W:
        fail("Radical 1 is %s but should be و" % rad1)
    if weakness in ("final-weak", "assimilated+final-weak"):
        if rad4 is not None:
            check_waw_ya(4, rad4)
        else:
            check_waw_ya(3, rad3)
    elif vform_supports_final_weak(form):
        if rad4 is not None:
            check_not_waw_ya(4, rad4)
        else:
            check_not_waw_ya(3, rad3)
    if weakness == "hollow":
        check_waw_ya(2, rad2)
    if weakness == "geminate":
        if rad4 is not None:
            fail("Internal error: No geminate quadrilaterals, should not be seen")
        if rad2 != rad3:
            fail("Weakness is geminate; radical 3 is %s but should be same as radical 2 %s" % (rad3, rad2))
    elif vform_supports_geminate(form):
        if rad4 is not None:
            fail("Internal error: No quadrilaterals should support geminate verbs")
        if rad2 == rad3 and not is_waw_ya(rad2) and (form + ":" + rad1 + rad2 + rad3) not in _SOUND_ROOTS:
            fail(
                "Weakness is '%s'; radical 2 and 3 are same at %s but should not be; consider making weakness 'geminate'"
                % (weakness, rad2)
            )


_ARABIC_LETTER_RE = re.compile("[ء-ي]")


def _normalize_char(ch: str) -> str:
    if ch in (HAMZA_ON_ALIF, HAMZA_UNDER_ALIF, HAMZA_ON_W, HAMZA_ON_Y):
        return HAMZA
    if ch == AMAQ:
        return Y
    if ch == ALIF:
        raise MaziniError(
            "bad_root",
            "Root contains alif (ا) which is not a valid root radical. For weak verbs, use و (waw) or ي (yaa) instead.",
        )
    return ch


def normalize_root(root: str) -> list[str]:
    """normalize_root: "كتب", "ك ت ب" or "ك_ت_ب" → the radicals, hamza seats folded to ء and ى to ي.

    Diacritics and non-Arabic characters in an unseparated root are dropped, as on the wiki.
    """
    if not root:
        raise MaziniError("bad_root", "Missing root")
    root = root.replace(AMAD, HAMZA + ALIF).replace(" ", "_")
    if "_" not in root:
        parts = [_normalize_char(ch) for ch in _ARABIC_LETTER_RE.findall(root)]
    else:
        parts = [_normalize_char(p) for p in root.split("_")]
    for p in parts:
        if len(p) != 1:
            raise MaziniError("bad_root", "Each radical must be one letter, saw '%s'" % p)
    if len(parts) not in (3, 4):
        raise MaziniError("bad_root", "A root needs three or four radicals, saw %d in '%s'" % (len(parts), root))
    return parts
