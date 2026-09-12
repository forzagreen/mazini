"""The engine-only half of وحدة:ar-verb/مختبر (wiki/batch_0.lua upstream), ported case for case."""

import pytest

from mazini import SLOTS, WAZNS, MaziniError, classify_triliteral_verb, conjugate, normalize_root


def slot(c, name):
    forms = c.slots.get(name)
    return "/".join(f.form for f in forms) if forms else None


def first(c, name):
    forms = c.slots.get(name)
    return forms[0].form if forms else None


def test_form_i():
    r = conjugate("كتب", "فعَل يفعُل")
    assert [first(r, s) for s in ("past_3ms", "ind_3ms", "imp_2ms", "ap", "pp")] == [
        "كَتَبَ",
        "يَكْتُبُ",
        "اُكْتُبْ",
        "كَاتِب",
        "مَكْتُوب",
    ]
    assert r.has_active and r.has_passive and r.verb_forms[0] == "I"


def test_forms_ii_iii_iv():
    r = conjugate("درس", "فعّل")
    assert [first(r, s) for s in ("past_3ms", "ind_3ms", "imp_2ms", "ap", "pp", "vn")] == [
        "دَرَّسَ",
        "يُدَرِّسُ",
        "دَرِّسْ",
        "مُدَرِّس",
        "مُدَرَّس",
        "تَدْرِيس",
    ]
    r = conjugate("قتل", "فاعل")
    assert [first(r, s) for s in ("past_3ms", "ind_3ms", "imp_2ms", "ap", "pp")] == [
        "قَاتَلَ",
        "يُقَاتِلُ",
        "قَاتِلْ",
        "مُقَاتِل",
        "مُقَاتَل",
    ]
    r = conjugate("رسل", "أفعل")
    assert [first(r, s) for s in ("past_3ms", "ind_3ms", "imp_2ms", "ap", "pp")] == [
        "أَرْسَلَ",
        "يُرْسِلُ",
        "أَرْسِلْ",
        "مُرْسِل",
        "مُرْسَل",
    ]


def test_form_iv_hollow_and_sound_exceptions():
    assert first(conjugate("قول", "أفعل"), "past_3ms") == "أَقَالَ"
    for root, want in [("تيس", "أَتَاسَ"), ("طيب", "أَطَابَ"), ("بين", "أَبَانَ"), ("ضيع", "أَضَاعَ"), ("طيح", "أَطَاحَ")]:
        assert first(conjugate(root, "أفعل"), "past_3ms") == want, root
    assert first(conjugate("تيس", "استفعل"), "past_3ms") == "اِسْتَتَاسَ"
    for root, want in [
        ("خيل", "أَخْيَلَ"),
        ("غيل", "أَغْيَلَ"),
        ("حيج", "أَحْيَجَ"),
        ("حين", "أَحْيَنَ"),
        ("خيف", "أَخْيَفَ"),
        ("ريف", "أَرْيَفَ"),
        ("زين", "أَزْيَنَ"),
    ]:
        assert first(conjugate(root, "أفعل"), "past_3ms") == want, root


def test_weak_and_root_spellings():
    qwl = conjugate("قول", "فعَل يفعُل")
    assert [first(qwl, s) for s in ("past_3ms", "ind_3ms", "imp_2ms")] == ["قَالَ", "يَقُولُ", "قُلْ"]
    rmy = conjugate("رمي", "فعَل يفعِل")
    assert [first(rmy, s) for s in ("past_3ms", "ind_3ms", "imp_2ms", "ap")] == ["رَمَى", "يَرْمِي", "اِرْمِ", "رَامٍ"]
    assert first(conjugate("م_د_د", "فعَل يفعُل"), "past_3ms") == "مَدَّ"
    wsl = conjugate("وصل", "فعَل يفعِل")
    assert [first(wsl, s) for s in ("past_3ms", "ind_3ms", "imp_2ms")] == ["وَصَلَ", "يَصِلُ", "صِلْ"]
    for root in ("ك_ت_ب", "ك ت ب", "كتب", "كَتَبَ"):
        assert first(conjugate(root, "فعَل يفعُل"), "past_3ms") == "كَتَبَ", root
    assert normalize_root("أخذ") == ["ء", "خ", "ذ"]
    assert normalize_root("رمى") == ["ر", "م", "ي"]


@pytest.mark.parametrize(
    "root,wazn,reduced,code",
    [
        ("قال", "فعَل يفعُل", False, "bad_root"),
        ("", "فعَل يفعُل", False, "bad_root"),
        ("كتب", "فعل", False, "unknown_wazn"),
        ("كتب", "انفعل", True, "reduced_not_applicable"),
    ],
)
def test_errors_have_stable_codes(root, wazn, reduced, code):
    with pytest.raises(MaziniError) as e:
        conjugate(root, wazn, reduced=reduced)
    assert e.value.code == code


def test_every_pattern():
    cases = [
        ("كتب", "فعَل يفعُل", "كَتَبَ", "يَكْتُبُ", "اُكْتُبْ"),
        ("ضرب", "فعَل يفعِل", "ضَرَبَ", "يَضْرِبُ", "اِضْرِبْ"),
        ("فتح", "فعَل يفعَل", "فَتَحَ", "يَفْتَحُ", "اِفْتَحْ"),
        ("علم", "فعِل يفعَل", "عَلِمَ", "يَعْلَمُ", "اِعْلَمْ"),
        ("كرم", "فعُل يفعُل", "كَرُمَ", "يَكْرُمُ", "اُكْرُمْ"),
        ("حسب", "فعِل يفعِل", "حَسِبَ", "يَحْسِبُ", "اِحْسِبْ"),
    ]
    for root, wazn, past, pres, imp in cases:
        r = conjugate(root, wazn)
        assert [slot(r, "past_3ms"), slot(r, "ind_3ms"), slot(r, "imp_2ms")] == [past, pres, imp], root
    derived = [
        ("علم", "تفعّل", "تَعَلَّمَ", "يَتَعَلَّمُ", "تَعَلُّم"),
        ("عون", "تفاعل", "تَعَاوَنَ", "يَتَعَاوَنُ", "تَعَاوُن"),
        ("كسر", "انفعل", "اِنْكَسَرَ", "يَنْكَسِرُ", "اِنْكِسَار"),
        ("جمع", "افتعل", "اِجْتَمَعَ", "يَجْتَمِعُ", "اِجْتِمَاع"),
        ("حمر", "افعلّ", "اِحْمَرَّ", "يَحْمَرُّ", "اِحْمِرَار"),
        ("خرج", "استفعل", "اِسْتَخْرَجَ", "يَسْتَخْرِجُ", "اِسْتِخْرَاج"),
        ("حمر", "افعالّ", "اِحْمَارَّ", "يَحْمَارُّ", "اِحْمِيرَار"),
        ("عشب", "افعوعل", "اِعْشَوْشَبَ", "يَعْشَوْشِبُ", "اِعْشِيشَاب"),
        ("جلذ", "افعوّل", "اِجْلَوَّذَ", "يَجْلَوِّذُ", "اِجْلِوَّاذ"),
        ("دحرج", "فعلل", "دَحْرَجَ", "يُدَحْرِجُ", "دَحْرَجَة"),
        ("دحرج", "تفعلل", "تَدَحْرَجَ", "يَتَدَحْرَجُ", "تَدَحْرُج"),
        ("حرجم", "افعنلل", "اِحْرَنْجَمَ", "يَحْرَنْجِمُ", "اِحْرِنْجَام"),
        ("قشعر", "افعللّ", "اِقْشَعَرَّ", "يَقْشَعِرُّ", "اِقْشِعْرَار"),
    ]
    for root, wazn, past, pres, vn in derived:
        r = conjugate(root, wazn)
        assert [slot(r, "past_3ms"), slot(r, "ind_3ms"), slot(r, "vn")] == [past, pres, vn], root + " " + wazn
    for w in WAZNS:
        root = "دحرج" if w.verb_form.endswith("q") else "كتب"
        assert conjugate(root, w.wazn).slots == conjugate(root, w.form_code).slots
    assert len(SLOTS) == 119


def test_persons_moods_passive():
    r = conjugate("كتب", "فعَل يفعُل")
    for s, want in [
        ("past_1s", "كَتَبْتُ"),
        ("past_2ms", "كَتَبْتَ"),
        ("past_3fs", "كَتَبَتْ"),
        ("past_3fp", "كَتَبْنَ"),
        ("ind_1s", "أَكْتُبُ"),
        ("ind_2fs", "تَكْتُبِينَ"),
        ("ind_3mp", "يَكْتُبُونَ"),
        ("sub_3ms", "يَكْتُبَ"),
        ("juss_3ms", "يَكْتُبْ"),
        ("imp_2fs", "اُكْتُبِي"),
        ("imp_2mp", "اُكْتُبُوا"),
        ("imp_2fp", "اُكْتُبْنَ"),
        ("past_pass_3ms", "كُتِبَ"),
        ("ind_pass_3ms", "يُكْتَبُ"),
        ("sub_pass_3ms", "يُكْتَبَ"),
        ("juss_pass_3ms", "يُكْتَبْ"),
    ]:
        assert slot(r, s) == want, s
    r2 = conjugate("درس", "فعّل")
    assert [slot(r2, "past_pass_3ms"), slot(r2, "ind_pass_3ms")] == ["دُرِّسَ", "يُدَرَّسُ"]


def test_irregular_and_reduced():
    raa = conjugate("رأي", "فعَل يفعَل")
    assert [slot(raa, s) for s in ("past_3ms", "ind_3ms", "imp_2ms")] == ["رَأَى", "يَرَى", "رَ"]
    araa = conjugate("رأي", "أفعل")
    assert [slot(araa, s) for s in ("past_3ms", "ind_3ms")] == ["أَرَى", "يُرِي"]
    assert slot(conjugate("أكل", "فعَل يفعُل"), "imp_2ms") == "كُلْ"
    assert slot(conjugate("أخذ", "فعَل يفعُل"), "imp_2ms") == "خُذْ"
    amar = conjugate("أمر", "فعَل يفعُل")
    assert slot(amar, "imp_2ms") == "مُرْ/اُؤْمُرْ"
    assert amar.slots["imp_2ms"][1].footnotes == ("[used especially with a clitic such as {{m|ar|فَ}} or {{m|ar|وَ}}]",)
    assert amar.irregular
    saal = conjugate("سأل", "فعَل يفعَل")
    assert [slot(saal, "imp_2ms"), slot(saal, "juss_3ms")] == ["اِسْأَلْ/سَلْ", "يَسْأَلْ/يَسَلْ"]
    hayy = conjugate("حيي", "فعِل يفعَل")
    assert [slot(hayy, "past_3ms"), slot(hayy, "ind_3ms")] == ["حَيَّ/حَيِيَ", "يَحْيَا"]
    itt = conjugate("أخذ", "افتعل", reduced=True)
    assert [slot(itt, s) for s in ("past_3ms", "ind_3ms", "vn")] == ["اِتَّخَذَ", "يَتَّخِذُ", "اِتِّخَاذ"]
    assert slot(conjugate("درأ", "تفاعل", reduced=True), "past_3ms") == "اِدَّارَأَ"
    istaa = conjugate("طوع", "استفعل", reduced=True)
    assert [slot(istaa, "past_3ms"), slot(istaa, "ind_3ms")] == ["اِسْطَاعَ", "يَسْطِيعُ"]
    for root, wazn, past, pres, imp, ap in [
        ("وعد", "فعَل يفعِل", "وَعَدَ", "يَعِدُ", "عِدْ", "وَاعِد"),
        ("دعو", "فعَل يفعُل", "دَعَا", "يَدْعُو", "اُدْعُ", "دَاعٍ"),
        ("شوي", "فعَل يفعِل", "شَوَى", "يَشْوِي", "اِشْوِ", "شَاوٍ"),
        ("وقي", "فعَل يفعِل", "وَقَى", "يَقِي", "قِ", "وَاقٍ"),
    ]:
        r = conjugate(root, wazn)
        assert [slot(r, s) for s in ("past_3ms", "ind_3ms", "imp_2ms", "ap")] == [past, pres, imp, ap], root


def test_uncertain_slots_and_metadata():
    r = conjugate("كتب", "فعَل يفعُل")
    assert [(f.form, f.footnotes) for f in r.slots["vn"]] == [("?", ())]
    assert r.uncertain_slots == ["vn"]
    assert (
        r.lemma[0].form == "كَتَبَ" and r.weakness == "sound" and r.passive == "pass" and r.classification == "صحيح سالم"
    )
    stative = conjugate("علم", "فعِل يفعَل")
    assert stative.uncertain_slots == ["ap", "vn"] and stative.passive == "ipass"


def test_classify():
    cases = [
        ("ك", "ت", "ب", "صحيح سالم"),
        ("م", "د", "د", "صحيح مُضعَّف"),
        ("أ", "خ", "ذ", "صحيح مهموز الفاء"),
        ("س", "أ", "ل", "صحيح مهموز العين"),
        ("ق", "ر", "أ", "صحيح مهموز اللام"),
        ("أ", "ب", "أ", "صحيح مهموز الفاء واللام"),
        ("أ", "ب", "ب", "صحيح مُضعَّف مهموز الفاء"),
        ("و", "ج", "د", "معتل مثال واوي"),
        ("و", "ض", "أ", "معتل مثال واوي مهموز اللام"),
        ("ي", "س", "ر", "معتل مثال يائي"),
        ("ي", "أ", "س", "معتل مثال يائي مهموز العين"),
        ("ق", "و", "ل", "معتل أجوف واوي"),
        ("ب", "ي", "ع", "معتل أجوف يائي"),
        ("د", "ع", "و", "معتل ناقص واوي"),
        ("ر", "م", "ي", "معتل ناقص يائي"),
        ("و", "ي", "ي", "معتل لفيف مقرون مُضعَّف يائي"),
        ("ح", "و", "و", "معتل لفيف مقرون مُضعَّف واوي"),
        ("ح", "و", "ي", "معتل لفيف مقرون"),
        ("أ", "و", "ي", "معتل لفيف مقرون مهموز الفاء"),
        ("و", "ق", "ي", "معتل لفيف مفروق"),
        ("و", "أ", "ي", "معتل لفيف مفروق مهموز العين"),
        ("أ", "و", "ل", "معتل أجوف واوي مهموز الفاء"),
        ("ق", "و", "أ", "معتل أجوف واوي مهموز اللام"),
        ("أ", "ي", "ب", "معتل أجوف يائي مهموز الفاء"),
        ("ج", "ي", "أ", "معتل أجوف يائي مهموز اللام"),
        ("ر", "أ", "و", "معتل ناقص واوي مهموز العين"),
        ("ش", "أ", "ي", "معتل ناقص يائي مهموز العين"),
        ("و", "د", "د", "معتل مثال واوي مُضعَّف"),
        ("ي", "ن", "ن", "معتل مثال يائي مُضعَّف"),
        ("و", "أ", "ب", "معتل مثال واوي مهموز العين"),
        ("أ", "ت", "ي", "معتل ناقص يائي مهموز الفاء"),
    ]
    for a, b, c, want in cases:
        assert classify_triliteral_verb(a, b, c) == want, a + b + c
