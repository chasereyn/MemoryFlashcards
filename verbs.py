"""
Spanish verb practice deck: load config + CSV, then for each verb emit 3 unique
(construction, subject) flashcards, seeded by year+month+verb. Each construction
isolates its own English/Spanish logic in one builder function.
"""
from __future__ import annotations

import csv
import json
import os
import random
import re
from dataclasses import dataclass
from datetime import date
from typing import Callable, Dict, List, Optional, Tuple

# —— 7 English “subjects” → Latin American Spanish person keys
SPANISH_PERSON_KEYS = ["yo", "tu", "ud", "nosotros", "uds"]
ENGLISH_PRONOUNS = ["I", "you", "he", "it", "we", "they", "you guys"]
SPANISH_MAP = [0, 1, 2, 2, 3, 4, 4]
_REFLEXIVE_CLITIC_BY_KEY = {
    "yo": "me",
    "tu": "te",
    "ud": "se",
    "nosotros": "nos",
    "uds": "se",
}
GERUND_AUXILIARIES = ("llevar", "seguir", "andar")
VALID_FLAGS = frozenset(
    {
        "preterite-yo",
        "preterite-el",
        "llevar",
        "seguir",
        "andar",
        "acabar",
        "questions",
    }
)
# Known construction ids, order used only for stable sorting. Add new ids at the end.
CONSTRUCTION_ORDER: Tuple[str, ...] = (
    "preterite",
    "llevar",
    "seguir",
    "andar",
    "acabar",
    "questions",
)
Flashcard = Tuple[str, str]  # (english, spanish,)


@dataclass
class VerbContext:
    """Per-verb + global runtime for builders (all config-driven, no hardcoded verb list)."""
    flags: dict
    auxiliary_data: Dict[str, dict]  # lemma -> loaded JSON
    acabar_data: Optional[dict]
    verbs_dir: str
    rotation_seed: str  # "YYYY-MM"
    wh_choice: str
    stative: bool
    acabar_de_english: str  # "past" | "ing" from CSV


# --------------------------------------------------------------------------- #
# JSON + English / Spanish form helpers
# --------------------------------------------------------------------------- #


def _verb_json_filename(verb: str) -> str:
    return (
        verb.replace("ñ", "n")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )


def load_verb_json(verb: str, verbs_dir: str = "verbs") -> Optional[dict]:
    for candidate in [verb, _verb_json_filename(verb)]:
        path = os.path.join(verbs_dir, f"{candidate}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Could not load {path}: {e}")
                return None
    return None


def _is_reflexive_infinitivo(json_data: dict) -> bool:
    inf = (json_data.get("infinitivo") or "").strip().lower()
    return inf.endswith(("arse", "erse", "irse"))


def _spanish_reflexive_infinitive_for_person(json_data: dict, spanish_key: str) -> str:
    inf = (json_data.get("infinitivo") or "").strip()
    if not _is_reflexive_infinitivo(json_data) or not inf or len(inf) < 4:
        return inf
    if not inf.lower().endswith("se"):
        return inf
    stem = inf[:-2]
    clitic = _REFLEXIVE_CLITIC_BY_KEY.get(spanish_key, "")
    if not clitic:
        return inf
    return f"{stem}{clitic}"


def _spanish_gerund_for_auxiliary_reflexive(gerund: str) -> str:
    g = gerund.strip()
    lower = g.lower()
    if lower.endswith("yéndose"):
        return g[:-7] + "yendo"
    if lower.endswith("iéndose"):
        return g[:-7] + "iendo"
    if lower.endswith("éndose"):
        return g[:-6] + "iendo"
    if lower.endswith("ándose"):
        return g[:-6] + "ando"
    return g


def _primary_english_verb_gloss(english_infinitivo: str) -> str:
    s = english_infinitivo.strip()
    if not s:
        return ""
    if s.lower().startswith("to "):
        s = s[3:].strip()
    main = s.split(";")[0].strip()
    if "," in main:
        main = main.split(",")[0].strip()
    if "(" in main:
        main = main.split("(")[0].strip()
    return main


def _get_english_base(json_data: dict) -> str:
    eng = json_data.get("english", {}) or {}
    inf_en = eng.get("infinitivo", "")
    if isinstance(inf_en, str) and inf_en.strip():
        return _primary_english_verb_gloss(inf_en)
    inf = json_data.get("infinitivo", "")
    if isinstance(inf, str):
        return inf.strip()
    return ""


def _derive_3rd_person(base: str) -> str:
    if not base:
        return ""
    if base.endswith(("s", "x", "z", "ch", "sh")):
        return base + "es"
    if base.endswith("y") and len(base) > 1 and base[-2] not in "aeiou":
        return base[:-1] + "ies"
    return base + "s"


def _derive_simple_past(base: str) -> str:
    if not base:
        return ""
    if base.endswith("e"):
        return base + "d"
    if base.endswith("y") and len(base) > 1 and base[-2] not in "aeiou":
        return base[:-1] + "ied"
    if len(base) >= 2 and base[-1] in "bdgmnprt" and base[-2] in "aeiou":
        return base + base[-1] + "ed"
    return base + "ed"


def _get_english_past_participle(json_data: dict) -> str:
    eng = json_data.get("english", {}) or {}
    pp = (eng.get("participioPasado") or "").strip()
    if pp:
        return pp
    base = _get_english_base(json_data)
    if not base:
        return ""
    if base.endswith("e"):
        return base + "d"
    if base.endswith("y") and len(base) > 1 and base[-2] not in "aeiou":
        return base[:-1] + "ied"
    return base + "ed"


def _get_gerund(json_data: dict) -> str:
    return (json_data.get("english", {}) or {}).get("gerundio", "") or ""


def _get_3rd_person(json_data: dict, prefs: dict) -> str:
    from_json = (json_data.get("english", {}) or {}).get("thirdPersonSingular", "") or ""
    from_json = from_json.strip()
    if from_json:
        return from_json
    override = (prefs.get("en_3rd_person") or "").strip()
    if override:
        return override
    return _derive_3rd_person(_get_english_base(json_data))


def _get_simple_past(json_data: dict, prefs: dict) -> str:
    override = (prefs.get("en_past") or "").strip()
    if override:
        return override
    preterito_desc = (json_data.get("english", {}) or {}).get("indicativo", {}) or {}
    preterito_desc = (preterito_desc.get("preterito", "") or "").strip() if isinstance(
        preterito_desc, dict
    ) else ""
    if isinstance(preterito_desc, str) and preterito_desc.lower().startswith("i "):
        parts = preterito_desc.split(None, 1)
        if len(parts) == 2:
            return parts[1].strip()
    return _derive_simple_past(_get_english_base(json_data))


def _get_spanish_conjugation(json_data: dict, tense: str, person_key: str) -> str:
    try:
        tense_data = (json_data.get("indicativo", {}) or {}).get(tense, {}) or {}
        return (tense_data.get(person_key, "") or "").strip()
    except (AttributeError, TypeError):
        return ""


def _prefs_from_context(ctx: VerbContext) -> dict:
    return {
        "es_present_style": "progressive",
        "stative_english": ctx.stative,
        "acabar_de_english": ctx.acabar_de_english,
        "rotation_seed": ctx.rotation_seed,
    }


def _get_english_preterite_1st(json_data: dict) -> str:
    p = (json_data.get("english", {}) or {}).get("indicativo", {}) or {}
    p = p.get("preterito", "")
    if isinstance(p, str) and p.strip().lower().startswith("i "):
        return p.strip()
    base = _get_english_base(json_data)
    past = _derive_simple_past(base)
    return f"I {past}" if past else ""


# --------------------------------------------------------------------------- #
# English line formatters (used by builders)
# --------------------------------------------------------------------------- #


def format_english_preterite(
    person_index: int, json_data: dict, prefs: dict
) -> str:
    pronoun = ENGLISH_PRONOUNS[person_index]
    verb_form = _get_simple_past(json_data, prefs)
    return f"{pronoun} {verb_form}"


def format_english_present_progressive(
    person_index: int, json_data: dict, prefs: dict
) -> str:
    gerund = _get_gerund(json_data)
    if not gerund:
        base = _get_english_base(json_data)
        gerund = base + "ing" if not base.endswith("e") else base[:-1] + "ing"
    pron = ENGLISH_PRONOUNS[person_index]
    if person_index == 0:
        return f"I'm {gerund}"
    if person_index == 1:
        return f"you're {gerund}"
    if person_index in (2, 3):
        return f"he's {gerund}" if person_index == 2 else f"it's {gerund}"
    if person_index == 4:
        return f"we're {gerund}"
    return f"they're {gerund}" if person_index == 5 else f"you guys are {gerund}"


def format_english_present_simple(
    person_index: int, json_data: dict, prefs: dict
) -> str:
    pronoun = ENGLISH_PRONOUNS[person_index]
    base = _get_english_base(json_data)
    if person_index in (2, 3):
        v = _get_3rd_person(json_data, prefs)
    else:
        v = base
    return f"{pronoun} {v}"


def format_english_llevar_gerund(
    person_index: int, json_data: dict, prefs: dict
) -> str:
    g = _get_gerund(json_data) or _derive_english_gerund_from_base(json_data)
    if not g:
        base = _get_english_base(json_data)
        g = base + "ing" if not base.endswith("e") else base[:-1] + "ing"
    if person_index == 0:
        return f"I've been {g}"
    if person_index == 1:
        return f"you've been {g}"
    if person_index in (2, 3):
        return f"he's been {g}" if person_index == 2 else f"it's been {g}"
    if person_index == 4:
        return f"we've been {g}"
    return f"they've been {g}" if person_index == 5 else f"you guys have been {g}"


def format_english_llevar_stative(
    person_index: int, json_data: dict, prefs: dict
) -> str:
    pp = _get_english_past_participle(json_data)
    if not pp:
        return format_english_llevar_gerund(person_index, json_data, prefs)
    if person_index == 0:
        return f"I've {pp}"
    if person_index == 1:
        return f"you've {pp}"
    if person_index in (2, 3):
        return f"he's {pp}" if person_index == 2 else f"it's {pp}"
    if person_index == 4:
        return f"we've {pp}"
    if person_index == 5:
        return f"they've {pp}"
    return f"you guys have {pp}"


def format_english_seguir_gerund(
    person_index: int, json_data: dict, prefs: dict
) -> str:
    g = _get_gerund(json_data) or _derive_english_gerund_from_base(json_data)
    if not g:
        base = _get_english_base(json_data)
        g = base + "ing" if not base.endswith("e") else base[:-1] + "ing"
    if person_index == 0:
        return f"I'm still {g}"
    if person_index == 1:
        return f"you're still {g}"
    if person_index in (2, 3):
        return f"he's still {g}" if person_index == 2 else f"it's still {g}"
    if person_index == 4:
        return f"we're still {g}"
    if person_index == 5:
        return f"they're still {g}"
    return f"you guys are still {g}"


def format_english_seguir_stative(
    person_index: int, json_data: dict, prefs: dict
) -> str:
    p = ENGLISH_PRONOUNS[person_index]
    base = _get_english_base(json_data)
    v = _get_3rd_person(json_data, prefs) if person_index in (2, 3) else base
    return f"{p} still {v}"


def format_english_andar_gerund(
    person_index: int, json_data: dict, prefs: dict, *, right_now_first: bool
) -> str:
    core = format_english_present_progressive(person_index, json_data, prefs)
    if right_now_first:
        return f"right now {core}"
    return f"{core} right now"


def format_english_andar_stative(
    person_index: int, json_data: dict, prefs: dict, *, right_now_first: bool
) -> str:
    core = format_english_present_simple(person_index, json_data, prefs)
    if right_now_first:
        return f"right now {core}"
    return f"{core} right now"


def _title_subject_pronoun(person_index: int) -> str:
    p = ENGLISH_PRONOUNS[person_index]
    if p == "you guys":
        return "You guys"
    if len(p) == 1:
        return p.upper()
    return p[0].upper() + p[1:]


def _derive_english_gerund_from_base(json_data: dict) -> str:
    g = _get_gerund(json_data)
    if g:
        return g
    base = _get_english_base(json_data)
    if not base:
        return ""
    if base.endswith("e"):
        return base[:-1] + "ing"
    return base + "ing"


def _parse_acabar_de_english_cell(raw: str) -> str:
    s = (raw or "").strip().lower()
    if not s or s in ("past", "preterite", "simple", "p"):
        return "past"
    if s in ("ing", "gerund", "g", "finished", "i"):
        return "ing"
    return "past"


def format_english_acabar_de(
    person_index: int, json_data: dict, prefs: dict
) -> str:
    subj = _title_subject_pronoun(person_index)
    style = _parse_acabar_de_english_cell(
        str(prefs.get("acabar_de_english", "") or "past")
    )
    if style == "ing":
        ger = _derive_english_gerund_from_base(json_data)
        if not ger:
            sp = _get_simple_past(json_data, prefs)
            return f"{subj} just {sp}" if sp else f"{subj} just (…)"
        return f"{subj} just finished {ger}"
    sp = _get_simple_past(json_data, prefs)
    if not sp:
        g = _derive_english_gerund_from_base(json_data)
        if g:
            return f"{subj} just finished {g}"
        return f"{subj} just (…)"
    return f"{subj} just {sp}"


def _parse_stative_csv_cell(raw: str) -> bool:
    s = (raw or "").strip().lower()
    if not s or s in ("0", "no", "n", "false"):
        return False
    return s in ("1", "true", "yes", "y", "stative")


# --------------------------------------------------------------------------- #
# Question (preterite) English / Spanish
# --------------------------------------------------------------------------- #


def _wh_fragment_to_english_prefix(wh_sp: str) -> Optional[str]:
    if not (wh_sp or "").strip():
        return None
    key = wh_sp.strip().lower()
    table = {
        "cuándo": "When",
        "dónde": "Where",
        "adónde": "Where",
        "qué": "What",
        "cómo": "How",
        "por qué": "Why",
        "para qué": "What for",
        "a quién": "Who",
        "con quién": "Who",
        "de qué": "What",
        "en qué": "What",
        "de dónde": "__de_donde__",
    }
    return table.get(key, wh_sp.strip().capitalize())


def _question_subject_pronoun(person_index: int) -> str:
    p = ENGLISH_PRONOUNS[person_index]
    return p if p == "I" else p.lower()


def _english_preterite_question_line(
    person_index: int, json_data: dict, wh_sp: str
) -> str:
    pron = _question_subject_pronoun(person_index)
    es_inf = (json_data.get("infinitivo", "") or "").strip().lower()
    base = _get_english_base(json_data)
    wh_raw = (wh_sp or "").strip().lower()
    wh_en = _wh_fragment_to_english_prefix(wh_sp)

    def was_were_aux(idx: int) -> str:
        return "were" if idx in (1, 4, 5, 6) else "was"

    if es_inf == "ser" or es_inf == "estar":
        aux = was_were_aux(person_index)
        if not wh_en:
            return f"{aux.capitalize()} {pron}?"
        if wh_raw == "cómo":
            return f"How {aux} {pron}?"
        if wh_raw in ("dónde", "adónde"):
            return f"Where {aux} {pron}?"
        if wh_raw == "cuándo":
            return f"When {aux} {pron}?"
        if wh_en and wh_en != "__de_donde__":
            return f"{wh_en} {aux} {pron}?"
        return f"{aux.capitalize()} {pron}?"

    if not base:
        return ""
    if wh_raw == "de dónde":
        return f"Where did {pron} {base} from?"
    if wh_raw == "con quién":
        return f"Who did {pron} {base} with?"
    if wh_raw in ("de qué", "en qué"):
        return f"What did {pron} {base} about?"
    if not wh_en:
        return f"Did {pron} {base}?"
    return f"{wh_en} did {pron} {base}?"


def _spanish_preterite_question(wh_fragment: str, conjugated: str) -> str:
    w = (wh_fragment or "").strip()
    if w:
        return f"¿{w} {conjugated}?"
    return f"¿{conjugated}?"


# --------------------------------------------------------------------------- #
# One function per construction: (verb, subject) -> optional flashcard
# --------------------------------------------------------------------------- #


def build_preterite(
    verb: str, subject: int, json_data: dict, ctx: VerbContext
) -> Optional[Flashcard]:
    if not 0 <= subject <= 6:
        return None
    if not (ctx.flags.get("preterite-yo") or ctx.flags.get("preterite-el")):
        return None
    if not (
        _get_spanish_conjugation(json_data, "preterito", "yo")
        and _get_spanish_conjugation(json_data, "preterito", "ud")
        and _get_english_preterite_1st(json_data)
    ):
        return None
    prefs = _prefs_from_context(ctx)
    sk = SPANISH_PERSON_KEYS[SPANISH_MAP[subject]]
    sp = _get_spanish_conjugation(json_data, "preterito", sk)
    if not sp:
        return None
    en = format_english_preterite(subject, json_data, prefs)
    return (en, sp)


def _build_aux_gerund(
    aux_id: str, verb: str, subject: int, json_data: dict, ctx: VerbContext
) -> Optional[Flashcard]:
    if aux_id not in ctx.auxiliary_data or ctx.flags.get(aux_id, 0) != 1:
        return None
    g = (json_data.get("gerundio") or "").strip()
    if not g:
        return None
    prefs = _prefs_from_context(ctx)
    st = bool(prefs.get("stative_english"))
    sk = SPANISH_PERSON_KEYS[SPANISH_MAP[subject]]
    aux = ctx.auxiliary_data[aux_id]
    conj = _get_spanish_conjugation(aux, "presente", sk)
    if not conj:
        return None
    if _is_reflexive_infinitivo(json_data):
        cl = _REFLEXIVE_CLITIC_BY_KEY.get(sk, "")
        gs = _spanish_gerund_for_auxiliary_reflexive(g)
        if cl:
            sp = f"{cl} {conj} {gs}"
        else:
            sp = f"{conj} {gs}"
    else:
        sp = f"{conj} {g}"

    if aux_id == "llevar":
        en = format_english_llevar_stative(subject, json_data, prefs) if st else format_english_llevar_gerund(subject, json_data, prefs)
    elif aux_id == "seguir":
        en = format_english_seguir_stative(subject, json_data, prefs) if st else format_english_seguir_gerund(subject, json_data, prefs)
    elif aux_id == "andar":
        rseed = (prefs.get("rotation_seed") or "no-rotation").strip()
        rnf = random.Random(
            f"andar-order\t{rseed}\t{aux_id}\t{verb}\t{subject}"
        ).choice((True, False))
        en = (
            format_english_andar_stative(subject, json_data, prefs, right_now_first=rnf)
            if st
            else format_english_andar_gerund(subject, json_data, prefs, right_now_first=rnf)
        )
    else:
        return None
    return (en, sp)


def build_llevar(
    verb: str, subject: int, json_data: dict, ctx: VerbContext
) -> Optional[Flashcard]:
    return _build_aux_gerund("llevar", verb, subject, json_data, ctx)


def build_seguir(
    verb: str, subject: int, json_data: dict, ctx: VerbContext
) -> Optional[Flashcard]:
    return _build_aux_gerund("seguir", verb, subject, json_data, ctx)


def build_andar(
    verb: str, subject: int, json_data: dict, ctx: VerbContext
) -> Optional[Flashcard]:
    return _build_aux_gerund("andar", verb, subject, json_data, ctx)


def build_acabar(
    verb: str, subject: int, json_data: dict, ctx: VerbContext
) -> Optional[Flashcard]:
    if ctx.flags.get("acabar", 0) != 1 or not ctx.acabar_data:
        return None
    inf = (json_data.get("infinitivo") or "").strip()
    if not inf:
        return None
    prefs = _prefs_from_context(ctx)
    sk = SPANISH_PERSON_KEYS[SPANISH_MAP[subject]]
    aconj = _get_spanish_conjugation(ctx.acabar_data, "presente", sk)
    if not aconj:
        return None
    main = (
        _spanish_reflexive_infinitive_for_person(json_data, sk)
        if _is_reflexive_infinitivo(json_data)
        else inf
    )
    if not main:
        return None
    sp = f"{aconj} de {main}"
    en = format_english_acabar_de(subject, json_data, prefs)
    return (en, sp)


def build_questions(
    verb: str, subject: int, json_data: dict, ctx: VerbContext
) -> Optional[Flashcard]:
    if ctx.flags.get("questions", 0) != 1:
        return None
    if not 0 <= subject <= 6:
        return None
    sk = SPANISH_PERSON_KEYS[SPANISH_MAP[subject]]
    conj = _get_spanish_conjugation(json_data, "preterito", sk)
    if not conj:
        return None
    en = _english_preterite_question_line(subject, json_data, ctx.wh_choice)
    if not en:
        return None
    return (en, _spanish_preterite_question(ctx.wh_choice, conj))


# Registry: construction id -> builder. Add new constructions here and in CONSTRUCTION_ORDER.
CONSTRUCTION_BUILDERS: Dict[str, Callable[[str, int, dict, VerbContext], Optional[Flashcard]]] = {
    "preterite": build_preterite,
    "llevar": build_llevar,
    "seguir": build_seguir,
    "andar": build_andar,
    "acabar": build_acabar,
    "questions": build_questions,
}


def _enabled_constructions(
    flags: dict, auxiliary_data: Dict[str, dict], acabar_data: Optional[dict]
) -> List[str]:
    g_yo, g_el = flags.get("preterite-yo", 0), flags.get("preterite-el", 0)
    out: List[str] = []
    for cid in CONSTRUCTION_ORDER:
        if cid == "preterite" and (g_yo or g_el):
            out.append(cid)
        elif cid in GERUND_AUXILIARIES and cid in auxiliary_data and flags.get(cid, 0) == 1:
            out.append(cid)
        elif cid == "acabar" and flags.get("acabar", 0) == 1 and acabar_data is not None:
            out.append(cid)
        elif cid == "questions" and flags.get("questions", 0) == 1:
            out.append(cid)
    return [c for c in out if c in CONSTRUCTION_BUILDERS]


def _construction_order_key(c: str) -> int:
    try:
        return CONSTRUCTION_ORDER.index(c)
    except ValueError:
        return 9999


def pick_three_construction_subject_pairs(
    verb: str, year: int, month: int, available: List[str]
) -> List[Tuple[str, int]]:
    """
    up to 3 unique (construction_id, subject) pairs; deterministic from YYYY-MM + verb.
    """
    if not available:
        return []
    pool = [(c, s) for c in available for s in range(7)]
    rng = random.Random(f"{year:04d}-{month:02d}\t{verb}\tconstruction-subject")
    k = min(3, len(pool))
    chosen = sorted(rng.sample(pool, k), key=lambda p: (_construction_order_key(p[0]), p[1]))
    return chosen


def three_flashcards_for_verb(
    verb: str,
    json_data: dict,
    ctx: VerbContext,
    year: int,
    month: int,
    available: List[str],
) -> List[Flashcard]:
    """Pick 3 unique (construction, subject) pairs and build each card via its builder."""
    out: List[Flashcard] = []
    for cid, subj in pick_three_construction_subject_pairs(verb, year, month, available):
        fn = CONSTRUCTION_BUILDERS.get(cid)
        if not fn:
            continue
        card = fn(verb, subj, json_data, ctx)
        if card is not None:
            out.append(card)
    return out


# --------------------------------------------------------------------------- #
# Config + CSV
# --------------------------------------------------------------------------- #


def parse_verbs_config(config_path: str) -> dict:
    flags: dict = {}
    if not os.path.exists(config_path):
        return flags
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#") or ":" not in s:
                continue
            k, v = s.split(":", 1)
            k, v = k.strip(), v.strip()
            if k in VALID_FLAGS and v in ("0", "1"):
                flags[k] = int(v)
    return flags


def parse_verbs_config_rotation(config_path: str) -> Tuple[int, int]:
    y, m = date.today().year, date.today().month
    if not os.path.exists(config_path):
        return (y, m)
    rot: Optional[Tuple[int, int]] = None
    yf, mf = None, None
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#") or ":" not in s:
                continue
            k, v = s.split(":", 1)
            k, v = k.strip().lower(), v.strip()
            if k == "rotation":
                mo = re.match(r"^(\d{4})\s*[-/]\s*(\d{1,2})\s*$", v)
                if mo:
                    rot = (int(mo.group(1)), int(mo.group(2)))
            if k == "rotation-year" and v.isdigit():
                yf = int(v)
            if k == "rotation-month" and v.isdigit():
                mf = int(v)
    if rot is not None:
        y, m = rot[0], rot[1]
    if yf is not None:
        y = yf
    if mf is not None:
        m = mf
    m = max(1, min(12, m))
    return (y, m)


def load_verb_rows_from_csv(csv_path: str) -> List[Tuple[str, str, bool, str]]:
    rows: List[Tuple[str, str, bool, str]] = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        names = r.fieldnames or ()
        if "verb" not in names:
            raise ValueError("verbs.csv must have a 'verb' column")
        whk = "WH-choice" if "WH-choice" in names else (
            "wh-choice" if "wh-choice" in names else None
        )
        has_st, has_ac = "stative" in names, "acabar_de" in names
        for row in r:
            v = (row.get("verb") or "").strip()
            if not v:
                continue
            wh = (row.get(whk) or "").strip() if whk else ""
            st = _parse_stative_csv_cell(row.get("stative", "") or "") if has_st else False
            ac = _parse_acabar_de_english_cell((row.get("acabar_de") or "")) if has_ac else "past"
            rows.append((v, wh, st, ac))
    return rows


def _load_auxiliary_and_acabar(
    flags: dict, verbs_dir: str, config_path: str
) -> Tuple[Dict[str, dict], Optional[dict]]:
    aux: Dict[str, dict] = {}
    for a in GERUND_AUXILIARIES:
        if flags.get(a, 0) != 1:
            continue
        d = load_verb_json(a, verbs_dir)
        if d:
            aux[a] = d
        else:
            print(
                f"Warning: {a}:1 in {config_path} but {a}.json not found; "
                f"skipping {a}."
            )
    ac: Optional[dict] = None
    if flags.get("acabar", 0) == 1:
        ac = load_verb_json("acabar", verbs_dir)
        if not ac:
            print(
                f"Warning: acabar:1 in {config_path} but acabar.json not found; "
                "skipping acabar."
            )
    return aux, ac


# --------------------------------------------------------------------------- #
# Main generator (entry from main.py)
# --------------------------------------------------------------------------- #


def generate_preterite_13_flashcards(
    verbs_path: str = "verbs.txt",
    output_path: str = "data/verbs.txt",
    verbs_dir: str = "verbs",
    config_path: str = "verbs_config.txt",
    csv_path: str = "verbs.csv",
) -> None:
    if os.path.exists(config_path) and not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"'{config_path}' exists but '{csv_path}' is missing. Add the CSV or remove the config."
        )
    odir = os.path.dirname(output_path)
    if odir and not os.path.exists(odir):
        os.makedirs(odir, exist_ok=True)

    if not (os.path.exists(config_path) and os.path.exists(csv_path)):
        raise FileNotFoundError(
            f"Need both '{config_path}' and '{csv_path}' in the current layout."
        )

    flags = parse_verbs_config(config_path)
    year, month = parse_verbs_config_rotation(config_path)
    rotation_seed = f"{year:04d}-{month:02d}"
    auxiliary_data, acabar_data = _load_auxiliary_and_acabar(flags, verbs_dir, config_path)
    available = _enabled_constructions(flags, auxiliary_data, acabar_data)
    if len(available) < 1:
        print("Warning: No constructions enabled; output will be empty.")

    verb_rows = load_verb_rows_from_csv(csv_path)
    all_cards: List[Flashcard] = []
    missing_json: List[str] = []
    miss_pre: List[str] = []

    for v, wh, st, acde in verb_rows:
        jd = load_verb_json(v, verbs_dir)
        if jd is None:
            missing_json.append(v)
            continue
        if (flags.get("preterite-yo") or flags.get("preterite-el")) and not (
            _get_english_preterite_1st(jd)
            and _get_spanish_conjugation(jd, "preterito", "yo")
            and _get_spanish_conjugation(jd, "preterito", "ud")
        ):
            miss_pre.append(v)

        ctx = VerbContext(
            flags=flags,
            auxiliary_data=auxiliary_data,
            acabar_data=acabar_data,
            verbs_dir=verbs_dir,
            rotation_seed=rotation_seed,
            wh_choice=wh,
            stative=st,
            acabar_de_english=acde,
        )
        all_cards.extend(three_flashcards_for_verb(v, jd, ctx, year, month, available))

    if missing_json:
        print(f"Warning: No JSON for verb(s): {', '.join(missing_json)}")
    if miss_pre and (flags.get("preterite-yo") or flags.get("preterite-el")):
        print(
            f"Warning: incomplete preterite in JSON for: {', '.join(miss_pre)}"
        )

    with open(output_path, "w", encoding="utf-8") as f:
        for en, sp in all_cards:
            f.write(f"{en}\n{sp}\n\n")

