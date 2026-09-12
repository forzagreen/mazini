"""Characters, diacritics and the slot inventory. Port of module/ar-verb.lua:74-291.

Every constant is a code point given by its escape so that mark order is never at the
mercy of an editor's normalisation.
"""

from __future__ import annotations

import re

# hamza variants
HAMZA = "ء"  # ء
HAMZA_ON_ALIF = "أ"  # أ
HAMZA_ON_W = "ؤ"  # ؤ
HAMZA_UNDER_ALIF = "إ"  # إ
HAMZA_ON_Y = "ئ"  # ئ
HAMZA_ANY_RE = re.compile("[ءأإؤئ]")
HAMZA_PH = "￰"  # hamza placeholder

BORDER = "￲"
KEEP_W_PH = "￳"  # retained-wāw placeholder; see postprocess
KEEP_HAMZA_PH = "￴"  # quiescent-hamza placeholder
WAW_SEAT_PH = "￵"  # pre-seated hamza-on-wāw placeholder
NO_MADDA_PH = "￶"  # hamza held back from the madda rule

# diacritics
A = "َ"  # fatḥa
AN = "ً"  # fatḥatān
U = "ُ"  # ḍamma
UN = "ٌ"  # ḍammatān
I = "ِ"  # kasra  # noqa: E741
IN = "ٍ"  # kasratān
SK = "ْ"  # sukūn
SH = "ّ"  # šadda
DAGGER_ALIF = "ٰ"
#: Regex source for one diacritic other than šadda.
DIACRITIC_ANY_BUT_SH = "[ًٌٍَُِْٰ]"
#: Regex source for one short vowel.
AIU = "[َُِ]"

dia = {"a": A, "i": I, "u": U}
undia = {A: "a", I: "i", U: "u", "-": "-"}

# letters
ALIF = "ا"
AMAQ = "ى"
AMAD = "آ"
TAM = "ة"
T = "ت"
N = "ن"
W = "و"
Y = "ي"
S = "س"
M = "م"

# common combinations
AH = A + TAM
AA = A + ALIF
AAMAQ = A + AMAQ
AAH = AA + TAM
II = I + Y
UU = U + W
AY = A + Y
AW = A + W
AYSK = AY + SK
AWSK = AW + SK
NA = N + A
NI = N + I
AAN = AA + N
AANI = AA + NI
MA = M + A
MU = M + U
TA = T + A
TU = T + U
_I = ALIF + I
_U = ALIF + U

#: The 13 person/number codes, in the module's slot order (ar-verb.lua:197-211).
PERSON_NUMBERS: tuple[str, ...] = (
    "1s",
    "2ms",
    "2fs",
    "3ms",
    "3fs",
    "2d",
    "3md",
    "3fd",
    "1p",
    "2mp",
    "2fp",
    "3mp",
    "3fp",
)
#: The five imperative persons, in the same order.
IMP_PERSON_NUMBERS: tuple[str, ...] = tuple(p for p in PERSON_NUMBERS if p.startswith("2"))


def pn_index(pn: str) -> int:
    """Index of a person in the 13-slot affix arrays (never a literal number in the port)."""
    return PERSON_NUMBERS.index(pn)


def imp_index(pn: str) -> int:
    return IMP_PERSON_NUMBERS.index(pn)


#: The slots whose form is the verb's citation form, in order of preference.
POTENTIAL_LEMMA_SLOTS: tuple[str, ...] = ("past_3ms", "past_pass_3ms", "ind_3ms", "ind_pass_3ms", "imp_2ms")
#: Staging slots for the form-I participles and the form-III alternative مصدر.
UNSETTABLE_SLOTS: tuple[str, ...] = ("ap1", "ap2", "ap3", "apcd", "apan", "pp2", "vn2")
TENSES: tuple[str, ...] = ("past", "ind", "sub", "juss")


def _build_slots() -> tuple[str, ...]:
    slots = ["ap", "pp", "vn", *UNSETTABLE_SLOTS]
    for tense in TENSES:
        for voice in ("", "_pass"):
            for pn in PERSON_NUMBERS:
                slots.append(tense + voice + "_" + pn)
    for pn in IMP_PERSON_NUMBERS:
        slots.append("imp_" + pn)
    return tuple(slots)


#: Every slot the engine can fill, in table order (ar-verb.lua add_slots, 269-291).
SLOTS: tuple[str, ...] = _build_slots()
SLOT_SET = frozenset(SLOTS)
#: Slots a form-I verb may simply not have been told: shown as "?" rather than left empty.
SLOTS_THAT_MAY_BE_UNCERTAIN: tuple[str, ...] = ("vn", "ap")
