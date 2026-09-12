"""From a root and a form code to a Base ready to conjugate.

Port of the root-path subset of parse_indicator_spec (3350-3362), construct_verb_spec (4800-4816) and
detect_indicator_spec (3650-3932).
"""

from __future__ import annotations

from .base import Base, VowelSpec, new_base
from .chars import dia, undia
from .errors import MaziniError
from .radicals import (
    check_radicals,
    form_viii_join_ta,
    hayy_radicals,
    is_passive_only,
    vform_probably_full_passive,
    vform_probably_impersonal_passive,
    vform_probably_no_passive,
    weakness_from_radicals,
)  # fmt: skip
from .wazn import Vowels


def build_base(
    radicals: list[str], verb_form: str, vowels: Vowels | None, *, passive: bool = False, reduced: bool = False
) -> Base:
    """build_base: what parse_indicator_spec leaves behind for "ك_ت_ب<I/a~u.pass.reduced>"."""
    lemma = "_".join(radicals)
    conj_vowels = [VowelSpec(dia[vowels.past], dia[vowels.nonpast])] if vowels else []
    return new_base(lemma, verb_form, conj_vowels, passive=passive, reduced=reduced)


def detect_indicator_spec(base: Base) -> None:
    """detect_indicator_spec: radicals, weakness, passive type and the grouped vowels."""
    if not base.conj_vowels:
        base.conj_vowels = [VowelSpec("-", "-")]
    vform = base.verb_form
    base.quadlit = vform.endswith("q")

    rads = base.lemma.split("_")
    for vs in base.conj_vowels:
        ir4: str | None = None
        if len(rads) == 3 and all(len(r) == 1 for r in rads):
            ir1, ir2, ir3 = rads
        elif len(rads) == 4 and all(len(r) == 1 for r in rads):
            ir1, ir2, ir3, ir4 = rads
        else:
            # The Lua module would fall through to infer_radicals() here and mis-conjugate; the port refuses.
            raise MaziniError("bad_root", "A root needs three or four single-letter radicals: " + base.lemma)
        if not base.quadlit and ir4 is not None:
            raise MaziniError(
                "bad_root", "A four-letter root cannot take a triliteral form (%s): %s" % (vform, base.lemma)
            )
        if base.quadlit and ir4 is None:
            raise MaziniError(
                "bad_root", "A quadriliteral form (%s) needs a four-letter root: %s" % (vform, base.lemma)
            )
        weakness = weakness_from_radicals(vform, ir1, ir2, ir3, ir4, vs.past, vs.nonpast)
        if vform == "VIII":
            vs.form_viii_assim = form_viii_join_ta(ir1, base.reduced)

        if vform == "I" and not is_passive_only(base.passive) and (vs.past == "-" or vs.nonpast == "-"):
            raise MaziniError(
                "unknown_wazn",
                "Form I verb that isn't passive-only or final-weak must have past~non-past vowels specified",
            )

        vs.rad1, vs.rad2, vs.rad3 = ir1, ir2, ir3
        if base.quadlit:
            vs.rad4 = ir4
        vs.weakness = weakness

        check_radicals(vform, weakness, ir1, ir2, ir3, ir4 if base.quadlit else None)

        form_iii_vi_geminate = vform in ("III", "VI") and ir2 == ir3 and ir2 != "ي"
        hayy_i_x = hayy_radicals(ir1, ir2, ir3, vform) and vform in ("I", "X")
        if not (form_iii_vi_geminate or hayy_i_x) and vs.variant is not None:
            raise MaziniError("internal", "Variant value 'var:%s' not allowed in this context" % vs.variant)

    if vform == "I":
        # Regroup the vowels for display; a single past~non-past pair groups trivially.
        group_by_past: list[tuple[str, list[str]]] = []
        for vs in base.conj_vowels:
            past, nonpast = undia[vs.past], undia[vs.nonpast]
            for g in group_by_past:
                if g[0] == past:
                    if nonpast not in g[1]:
                        g[1].append(nonpast)
                    break
            else:
                group_by_past.append((past, [nonpast]))
        group_by_nonpast: list[tuple[list[str], list[str]]] = []
        for past, nonpasts in group_by_past:
            for h in group_by_nonpast:
                if h[1] == nonpasts:
                    if past not in h[0]:
                        h[0].append(past)
                    break
            else:
                group_by_nonpast.append(([past], nonpasts))
        base.grouped_conj_vowels = group_by_nonpast

    # Default the passive type (ar-verb.lua 3879-3897).
    if not base.passive:
        base.passive_defaulted = True
        if vform_probably_full_passive(vform):
            base.passive = "pass"
        else:
            base.passive_uncertain = True
            for vs in base.conj_vowels:
                if vform_probably_no_passive(vform, vs.past):
                    base.passive = "nopass"
                    break
                if vform_probably_impersonal_passive(vform, vs.past):
                    base.passive = "ipass"
                    break
            base.passive = base.passive or "pass"
