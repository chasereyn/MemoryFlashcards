"""Tests for English phrasing of Spanish verb auxiliary + gerund drills (stative column)."""
import os

import verbs
from verbs import (
    _parse_stative_csv_cell,
    _parse_acabar_de_english_cell,
    load_verb_json,
    load_verb_rows_from_csv,
    format_english_seguir_stative,
    format_english_llevar_stative,
    format_english_andar_stative,
    format_english_acabar_de,
)


def test_parse_stative_csv_cell():
    assert _parse_stative_csv_cell("") is False
    assert _parse_stative_csv_cell("0") is False
    assert _parse_stative_csv_cell("1") is True
    assert _parse_stative_csv_cell("true") is True
    assert _parse_stative_csv_cell("YES") is True
    assert _parse_stative_csv_cell("y") is True


def test_saber_stative_phrases():
    root = os.path.dirname(os.path.abspath(__file__))
    j = load_verb_json("saber", os.path.join(root, "verbs"))
    assert j is not None
    prefs = {"es_present_style": "progressive", "stative_english": True}
    s = format_english_seguir_stative(2, j, prefs)
    assert s == "he still knows", s
    assert "knowing" not in s
    s2 = format_english_llevar_stative(0, j, prefs)
    assert s2 == "I've known", s2
    assert "been knowing" not in s2
    a1 = format_english_andar_stative(0, j, prefs, right_now_first=True)
    assert a1.startswith("right now ")
    assert "know" in a1
    a2 = format_english_andar_stative(0, j, prefs, right_now_first=False)
    assert a2.endswith(" right now")
    assert " right now" in a2
    assert "I'm knowing" not in a1 + a2


def test_conocer_dynamic_vs_stative():
    root = os.path.dirname(os.path.abspath(__file__))
    j = load_verb_json("conocer", os.path.join(root, "verbs"))
    assert j is not None
    prefs = {"es_present_style": "progressive", "stative_english": False}
    d = verbs.format_english_seguir_gerund(2, j, prefs)
    assert "still" in d and "meeting" in d, d
    prefs["stative_english"] = True
    st = format_english_seguir_stative(2, j, prefs)
    assert st == "he still meets", st
    assert "meeting" not in st


def test_load_verb_rows_stative_column():
    root = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(root, "verbs.csv")
    rows = load_verb_rows_from_csv(p)
    by = {r[0]: (r[1], r[2], r[3]) for r in rows}
    assert by["saber"][1] is True
    assert by.get("hacer", (None, None, "past"))[1] is False
    assert by["saber"][2] == "past"


def test_acabar_de_english_past_and_ing():
    root = os.path.dirname(os.path.abspath(__file__))
    m = load_verb_json("manejar", os.path.join(root, "verbs"))
    assert m is not None
    v = load_verb_json("volver", os.path.join(root, "verbs"))
    assert v is not None
    prefs: dict = {"es_present_style": "progressive", "stative_english": False,
                     "acabar_de_english": "past"}
    s = format_english_acabar_de(0, m, prefs)
    assert s == "I just drove" or s.startswith("I just "), s
    prefs["acabar_de_english"] = "ing"
    s2 = format_english_acabar_de(0, m, prefs)
    assert "finished" in s2 and "driving" in s2, s2
    prefs["acabar_de_english"] = "past"
    s3 = format_english_acabar_de(3, v, prefs)
    assert s3 == "It just returned", s3


def test_parse_acabar_de_cell():
    assert _parse_acabar_de_english_cell("") == "past"
    assert _parse_acabar_de_english_cell("ing") == "ing"
    assert _parse_acabar_de_english_cell("GERUND") == "ing"


if __name__ == "__main__":
    test_parse_stative_csv_cell()
    test_saber_stative_phrases()
    test_conocer_dynamic_vs_stative()
    test_load_verb_rows_stative_column()
    test_parse_acabar_de_cell()
    test_acabar_de_english_past_and_ing()
    print("test_verbs_english: all passed")
