"""The comparison the book fixtures are checked with: a copy of tools/normalise.py upstream.

Not used by the engine (which never normalises); exported for tests and for anyone comparing
against printed forms.
"""

from __future__ import annotations

import re
import unicodedata

TATWEEL = "ـ"
SHADDA = "ّ"
SUKUN = "ْ"
FATHA, DAMMA, KASRA = "َ", "ُ", "ِ"
ALIF, WAW, YA, WASLA, ALIF_HAMZA = "ا", "و", "ي", "ٱ", "أ"
ALIF_HAMZA_BELOW = "إ"
WAW_HAMZA = "ؤ"
YA_HAMZA = "ئ"
MARK_RE = re.compile("[ً-ْٰ]")


def norm(s: str | None) -> str | None:
    """Canonical form: wikilinks and tags stripped, NFC, no tatweel, trimmed. None for an empty input."""
    if not s:
        return None
    s = re.sub(r"\[\[[^|\]]*\|([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = unicodedata.normalize("NFC", s).replace(TATWEEL, "")
    return s.strip()


def loose(s: str | None) -> str | None:
    """Fold the printing conventions on which a reference and Wiktionary legitimately differ."""
    s = norm(s)
    if s is None:
        return None
    s = s.replace(WASLA, ALIF)
    s = re.sub("^[" + ALIF_HAMZA + ALIF_HAMZA_BELOW + "]([" + DAMMA + KASRA + FATHA + "])", ALIF + r"\1", s)
    if s[:1] == ALIF_HAMZA_BELOW and not MARK_RE.match(s[1:2]):
        s = ALIF + KASRA + s[1:]
    s = re.sub("^" + ALIF + DAMMA + WAW_HAMZA + SUKUN, ALIF + DAMMA + WAW, s)
    s = re.sub("^" + ALIF + KASRA + YA_HAMZA + SUKUN, ALIF + KASRA + YA, s)
    s = re.sub(FATHA + "(" + SHADDA + "?)(" + ALIF + ")", r"\1\2", s)
    s = re.sub(DAMMA + "(" + SHADDA + "?)(" + WAW + ")(" + SUKUN + "?)", r"\1\2", s)
    s = re.sub(KASRA + "(" + SHADDA + "?)(" + YA + ")(" + SUKUN + "?)", r"\1\2", s)
    s = re.sub(SUKUN + "$", "", s)
    return s
