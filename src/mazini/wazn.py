"""The وزن names {{تصريف}} takes, their form codes and their مجرد/مزيد class. ar-verb.lua:140-195."""

from __future__ import annotations

import re
from dataclasses import dataclass

ALLOWED_VFORMS: tuple[str, ...] = (
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV",
    "Iq", "IIq", "IIIq", "IVq",
)  # fmt: skip


@dataclass(frozen=True, slots=True)
class Vowels:
    past: str
    nonpast: str


@dataclass(frozen=True, slots=True)
class WaznInfo:
    #: The pattern as Arabic grammar names it, e.g. فعَل يفعُل or استفعل.
    wazn: str
    form_code: str
    verb_form: str
    #: Form I only: the past and non-past stem vowels.
    vowels: Vowels | None
    #: مُجرَّد / مزيد بحرف / مزيد بحرفين / مزيد بثلاثة أحرف
    basic_deriv: str


_TABLE: list[tuple[str, str, str]] = [
    ("فعَل يفعُل", "I/a~u", "مُجرَّد"),
    ("فعَل يفعِل", "I/a~i", "مُجرَّد"),
    ("فعَل يفعَل", "I/a~a", "مُجرَّد"),
    ("فعُل يفعُل", "I/u~u", "مُجرَّد"),
    ("فعِل يفعَل", "I/i~a", "مُجرَّد"),
    ("فعِل يفعِل", "I/i~i", "مُجرَّد"),
    ("فعّل", "II", "مزيد بحرف"),
    ("فاعل", "III", "مزيد بحرف"),
    ("أفعل", "IV", "مزيد بحرف"),
    ("تفعّل", "V", "مزيد بحرفين"),
    ("تفاعل", "VI", "مزيد بحرفين"),
    ("انفعل", "VII", "مزيد بحرفين"),
    ("افتعل", "VIII", "مزيد بحرفين"),
    ("افعلّ", "IX", "مزيد بحرفين"),
    ("استفعل", "X", "مزيد بثلاثة أحرف"),
    ("افعالّ", "XI", "مزيد بثلاثة أحرف"),
    ("افعوعل", "XII", "مزيد بثلاثة أحرف"),
    ("افعوّل", "XIII", "مزيد بثلاثة أحرف"),
    ("فعلل", "Iq", "مُجرَّد"),
    ("تفعلل", "IIq", "مزيد بحرف"),
    ("افعنلل", "IIIq", "مزيد بحرفين"),  # "XIV" should not be used
    ("افعللّ", "IVq", "مزيد بحرفين"),
]

_FORM_I_RE = re.compile(r"^(I)/([aiu])~([aiu])$")


def parse_form_code(code: str) -> tuple[str, Vowels | None] | None:
    """Parse a form code such as "I/a~u" or "X" into its form and (for form I) vowels."""
    m = _FORM_I_RE.match(code)
    if m:
        return "I", Vowels(m.group(2), m.group(3))
    if code in ALLOWED_VFORMS and code != "I":
        return code, None
    return None


def _info(wazn: str, code: str, deriv: str) -> WaznInfo:
    parsed = parse_form_code(code)
    assert parsed is not None
    return WaznInfo(wazn, code, parsed[0], parsed[1], deriv)


#: The 22 patterns, in the module's order.
WAZNS: tuple[WaznInfo, ...] = tuple(_info(*row) for row in _TABLE)
WAZN_BY_NAME: dict[str, WaznInfo] = {w.wazn: w for w in WAZNS}
WAZN_BY_CODE: dict[str, WaznInfo] = {w.form_code: w for w in WAZNS}


def form_code_to_wazn(code: str) -> str | None:
    """The وزن a form code is displayed as; XIV and XV have none (ar-verb.lua:166-169)."""
    info = WAZN_BY_CODE.get(code)
    return info.wazn if info else None
