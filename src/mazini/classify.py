"""The infobox's «صحيح سالم / معتل أجوف واوي …» classification of a triliteral root.

Port of ar-verb.lua export.classify_triliteral_verb (4569-4731), branch for branch.
"""

from __future__ import annotations

from .chars import HAMZA, HAMZA_ON_ALIF, HAMZA_ON_W, HAMZA_ON_Y, HAMZA_UNDER_ALIF, W, Y

_HAMZAS = frozenset({HAMZA, HAMZA_ON_ALIF, HAMZA_UNDER_ALIF, HAMZA_ON_W, HAMZA_ON_Y})


def classify_triliteral_verb(r1: str, r2: str, r3: str) -> str:  # noqa: PLR0911
    h = [r1 in _HAMZAS, r2 in _HAMZAS, r3 in _HAMZAS]
    w = [r1 in (W, Y), r2 in (W, Y), r3 in (W, Y)]
    weak_count = sum(w)
    doubled = r2 == r3

    if weak_count > 0:
        if weak_count >= 2:
            if w[1] and w[2]:
                if doubled:
                    return "معتل لفيف مقرون مُضعَّف واوي" if r2 == W else "معتل لفيف مقرون مُضعَّف يائي"
                if h[0]:
                    return "معتل لفيف مقرون مهموز الفاء"
                return "معتل لفيف مقرون"
            if w[0] and w[1]:
                return "معتل لفيف مقرون"
            if w[0] and w[2]:
                if h[1]:
                    return "معتل لفيف مفروق مهموز العين"
                return "معتل لفيف مفروق"
        elif w[0]:
            if r1 == W:
                if h[2]:
                    return "معتل مثال واوي مهموز اللام"
                if doubled:
                    return "معتل مثال واوي مُضعَّف"
                if h[1]:
                    return "معتل مثال واوي مهموز العين"
                return "معتل مثال واوي"
            if doubled:
                return "معتل مثال يائي مُضعَّف"
            if h[1]:
                return "معتل مثال يائي مهموز العين"
            return "معتل مثال يائي"
        elif w[1]:
            if r2 == W:
                if h[2]:
                    return "معتل أجوف واوي مهموز اللام"
                if h[0]:
                    return "معتل أجوف واوي مهموز الفاء"
                return "معتل أجوف واوي"
            if h[2]:
                return "معتل أجوف يائي مهموز اللام"
            if h[0]:
                return "معتل أجوف يائي مهموز الفاء"
            return "معتل أجوف يائي"
        elif w[2]:
            if r3 == W:
                if h[0]:
                    return "معتل ناقص واوي مهموز الفاء"
                if h[1]:
                    return "معتل ناقص واوي مهموز العين"
                return "معتل ناقص واوي"
            if h[0]:
                return "معتل ناقص يائي مهموز الفاء"
            if h[1]:
                return "معتل ناقص يائي مهموز العين"
            return "معتل ناقص يائي"
    else:
        if h[0] or h[1] or h[2]:
            if h[0] and h[2]:
                return "صحيح مهموز الفاء واللام"
            if h[0]:
                return "صحيح مُضعَّف مهموز الفاء" if doubled else "صحيح مهموز الفاء"
            if h[1]:
                return "صحيح مهموز العين"
            return "صحيح مهموز اللام"
        if doubled:
            return "صحيح مُضعَّف"
        return "صحيح سالم"
    return "غير معروف"
