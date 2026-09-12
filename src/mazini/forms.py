"""Form objects and the subset of Module:inflection utilities the engine uses.

A "form object" is Form(form, footnotes); an "abbreviated form list" is a string, a Form, or a
list of either. Port of inflection utilities.lua 259-368, 416-425, 497-511, 613-643, 646-676,
717-766, 783-803 and ar-verb.lua q() 471-499.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace

Footnotes = tuple[str, ...] | None


@dataclass(frozen=True, slots=True)
class Form:
    form: str
    footnotes: Footnotes = None
    uncertain: bool = False


AbForm = str | Form
AbForms = AbForm | Sequence[AbForm]
FormTable = dict[str, list[Form]]


def is_form(x: object) -> bool:
    return isinstance(x, Form)


def combine_footnotes(notes1: Footnotes, notes2: Footnotes) -> Footnotes:
    """Union of two footnote lists, order kept, duplicates dropped (combine_footnotes)."""
    if not notes1 and not notes2:
        return None
    if not notes1:
        return notes2
    if not notes2:
        return notes1
    combined = list(notes1)
    for note in notes2:
        if note not in combined:
            combined.append(note)
    return tuple(combined)


def _notes(addl: str | Sequence[str] | None) -> Footnotes:
    if addl is None:
        return None
    if isinstance(addl, str):
        return (addl,)
    return tuple(addl)


def combine_form_and_footnotes(
    abform: AbForm, addl_footnotes: str | Sequence[str] | None = None, new_formval: str | None = None
) -> AbForm:
    """combine_form_and_footnotes: attach footnotes (and optionally a new form value) to an abbreviated form."""
    notes = _notes(addl_footnotes)
    if notes is None and new_formval is None:
        return abform
    if isinstance(abform, str):
        return Form(new_formval if new_formval is not None else abform, notes)
    out = abform
    if new_formval is not None:
        out = replace(out, form=new_formval)
    if notes is not None:
        out = replace(out, footnotes=combine_footnotes(out.footnotes, notes))
    return out


def to_general_list(abforms: AbForms, footnotes: str | Sequence[str] | None = None) -> list[Form]:
    """convert_to_general_list_form: an abbreviated form list as a list of form objects."""
    notes = _notes(footnotes)
    if isinstance(abforms, str):
        return [Form(abforms, notes)]
    if isinstance(abforms, Form):
        result = combine_form_and_footnotes(abforms, notes)
        return [result if isinstance(result, Form) else Form(result)]
    out: list[Form] = []
    for f in abforms:
        if isinstance(f, str):
            out.append(Form(f, notes))
        else:
            r = combine_form_and_footnotes(f, notes)
            out.append(r if isinstance(r, Form) else Form(r))
    return out


def insert_form_into_list(lst: list[Form], form: Form | None) -> None:
    """insert_form_into_list: append unless the same form value is already present (first occurrence wins)."""
    if form is None or form.form is None:
        return
    for listform in lst:
        if listform.form == form.form:
            # Footnote merging only happens for footnotes carrying a ! or + modifier, which the engine
            # never produces; the upstream branch is also unreachable (it references an undefined variable).
            return
    lst.append(form)


def insert_form(formtable: FormTable, slot: str, form: Form | None) -> None:
    if form is None or form.form is None:
        return
    if slot not in formtable:
        formtable[slot] = []
    insert_form_into_list(formtable[slot], form)


def insert_forms(formtable: FormTable, slot: str, forms: Sequence[Form] | None) -> None:
    if forms is None:
        return
    for form in forms:
        insert_form(formtable, slot, form)


def map_forms(forms: Sequence[Form] | None, fn: Callable[[str], str]) -> list[Form] | None:
    """map_forms: map a function over form values, keeping footnotes; "?" is passed through."""
    if forms is None:
        return None
    out: list[Form] = []
    for form in forms:
        newval = "?" if form.form == "?" else fn(form.form)
        insert_form_into_list(out, replace(form, form=newval))
    return out


def _combine(stem: str, ending: str, combine_stem_ending: Callable[[str, str], str]) -> str:
    if stem == "?" or ending == "?":
        return "?"
    return combine_stem_ending(stem, ending)


def add_forms(
    formtable: FormTable,
    slot: str,
    stems: AbForms | None,
    endings: AbForms | None,
    combine_stem_ending: Callable[[str, str], str],
    footnotes: Footnotes = None,
) -> None:
    """add_forms: every stem × every ending into `slot`, with footnotes unioned."""
    if stems is None or endings is None:
        return
    if isinstance(stems, str) and isinstance(endings, str):
        insert_form(formtable, slot, Form(_combine(stems, endings, combine_stem_ending), footnotes))
        return
    if isinstance(stems, str) and not isinstance(endings, Form) and all(isinstance(e, str) for e in endings):
        for ending in endings:
            insert_form(formtable, slot, Form(_combine(stems, ending, combine_stem_ending), footnotes))  # type: ignore[arg-type]
        return
    stem_list = to_general_list(stems)
    ending_list = to_general_list(endings, footnotes)
    for stem in stem_list:
        for ending in ending_list:
            notes: Footnotes
            if stem.footnotes and ending.footnotes:
                merged = list(stem.footnotes)
                for f in ending.footnotes:
                    if f not in merged:
                        merged.append(f)
                notes = tuple(merged)
            elif stem.footnotes:
                notes = stem.footnotes
            elif ending.footnotes:
                notes = ending.footnotes
            else:
                notes = None
            insert_form(formtable, slot, Form(_combine(stem.form, ending.form, combine_stem_ending), notes))


def add_multiple_forms(
    formtable: FormTable,
    slot: str,
    components: Sequence[AbForms | None],
    combine_stem_ending: Callable[[str, str], str],
    footnotes: Footnotes = None,
) -> None:
    """add_multiple_forms: reduce three or more components left to right through add_forms."""
    if len(components) == 0:
        return
    if len(components) == 1:
        if components[0] is None:
            return
        insert_forms(formtable, slot, to_general_list(components[0], footnotes))
        return
    if len(components) == 2:
        add_forms(formtable, slot, components[0], components[1], combine_stem_ending, footnotes)
        return
    prev: AbForms | None = components[0]
    for i in range(1, len(components)):
        temp: FormTable = {}
        add_forms(temp, slot, prev, components[i], combine_stem_ending, footnotes if i == len(components) - 1 else None)
        prev = temp.get(slot)
    insert_forms(formtable, slot, prev)  # type: ignore[arg-type]


def q(*args: AbForm) -> AbForm:
    """q(): concatenate strings and form objects. All strings → a string; otherwise a Form carrying the
    union of the footnotes (ar-verb.lua:471-499)."""
    for i, a in enumerate(args):
        if a is None:
            raise MaziniErrorInternal("Saw nil at index %d in q()" % (i + 1))
    if all(isinstance(a, str) for a in args):
        return "".join(args)  # type: ignore[arg-type]
    form = ""
    footnotes: Footnotes = None
    for a in args:
        if isinstance(a, str):
            form += a
        else:
            form += a.form
            footnotes = combine_footnotes(footnotes, a.footnotes)
    return Form(form, footnotes)


class MaziniErrorInternal(Exception):
    pass


def rget(rad: AbForm) -> str:
    """rget: the form value of a radical or vowel (a string or form object)."""
    return rad if isinstance(rad, str) else rad.form


def rget_footnotes(rad: AbForm) -> Footnotes:
    return None if isinstance(rad, str) else rad.footnotes


def req(rad: AbForm | None, val: str) -> bool:
    return rad is not None and rget(rad) == val


def map_vowel(vow: AbForm, fn: Callable[[str], str]) -> AbForm:
    """map_vowel: map the form value of a vowel, keeping footnotes."""
    return fn(vow) if isinstance(vow, str) else Form(fn(vow.form), vow.footnotes)
