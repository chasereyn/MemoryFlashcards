import csv
import json
import os
import random
from typing import Dict, List, Tuple, Optional


# Map for 7 English persons: I, you, he, it, we, they, you guys
# Spanish persons: yo, tu, ud, nosotros, uds (Latin American - uds for both they and you guys)
SPANISH_PERSON_KEYS = ['yo', 'tu', 'ud', 'nosotros', 'uds']
ENGLISH_PRONOUNS = ["I", "you", "he", "it", "we", "they", "you guys"]
SPANISH_MAP = [0, 1, 2, 2, 3, 4, 4]  # it=he, you guys=they

# LA 5-person grid for IOP drills (indices match SPANISH_PERSON_KEYS).
IOP_ENGLISH_SUBJECTS = ("I", "you", "he", "we", "they")
IOP_ENGLISH_OBJECTS = ("me", "you", "him", "us", "them")
IOP_SPANISH_CLITICS = ("me", "te", "le", "nos", "les")
# Preterite English verb between subject and IO object (e.g. decir -> "told").
IOP_VERB_ENGLISH_PRETERITE = {
    "decir": "told",
}


def _verb_json_filename(verb: str) -> str:
    """Resolve verb to JSON filename (handles ñ→n for filesystem compatibility)."""
    return verb.replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')


def load_verb_json(verb: str, verbs_dir: str = "verbs") -> Optional[dict]:
    """
    Load verb data from verbs/{verb}.json.
    Returns None if file doesn't exist.
    Handles ñ/accents in verb names (e.g. bañarse -> banyarse.json, añadir -> anyadir.json).
    """
    for candidate in [verb, _verb_json_filename(verb)]:
        path = os.path.join(verbs_dir, f"{candidate}.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Could not load {path}: {e}")
                return None
    return None


def _primary_english_verb_gloss(english_infinitivo: str) -> str:
    """
    One short English lemma for drills: first sense before ; or ,, strip 'to ',
    drop a parenthetical like '(a vehicle)'.
    """
    s = english_infinitivo.strip()
    if not s:
        return ''
    if s.lower().startswith('to '):
        s = s[3:].strip()
    main = s.split(';')[0].strip()
    if ',' in main:
        main = main.split(',')[0].strip()
    if '(' in main:
        main = main.split('(')[0].strip()
    return main


def _get_english_base(json_data: dict) -> str:
    """Base for English phrasing: primary gloss from english.infinitivo, else Spanish lemma."""
    eng = json_data.get('english', {}) or {}
    inf_en = eng.get('infinitivo', '')
    if isinstance(inf_en, str) and inf_en.strip():
        return _primary_english_verb_gloss(inf_en)
    inf = json_data.get('infinitivo', '')
    if isinstance(inf, str):
        return inf.strip()
    return ''


def _derive_3rd_person(base: str) -> str:
    """Derive 3rd person singular from base (e.g., 'go' -> 'goes'). Simple rules."""
    if not base:
        return ''
    if base.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return base + 'es'
    if base.endswith('y') and len(base) > 1 and base[-2] not in 'aeiou':
        return base[:-1] + 'ies'
    return base + 's'


def _derive_simple_past(base: str) -> str:
    """Derive simple past from base (e.g., 'talk' -> 'talked'). Simple rules."""
    if not base:
        return ''
    if base.endswith('e'):
        return base + 'd'
    if base.endswith('y') and len(base) > 1 and base[-2] not in 'aeiou':
        return base[:-1] + 'ied'
    if len(base) >= 2 and base[-1] in 'bdgmnprt' and base[-2] in 'aeiou':
        return base + base[-1] + 'ed'
    return base + 'ed'


def _get_gerund(json_data: dict) -> str:
    """Get English gerund from JSON."""
    return (json_data.get('english', {}).get('gerundio', '') or '').strip()


def _get_3rd_person(json_data: dict, prefs: dict) -> str:
    """Get 3rd person singular - from JSON, override, or derive."""
    from_json = (json_data.get('english', {}) or {}).get('thirdPersonSingular', '').strip()
    if from_json:
        return from_json
    override = prefs.get('en_3rd_person', '').strip()
    if override:
        return override
    base = _get_english_base(json_data)
    return _derive_3rd_person(base)


def _get_simple_past(json_data: dict, prefs: dict) -> str:
    """Get simple past - from override, JSON, or derive."""
    override = prefs.get('en_past', '').strip()
    if override:
        return override
    # Try to parse from english.indicativo.preterito (e.g., "I went" -> "went")
    preterito_desc = (json_data.get('english', {}).get('indicativo', {}) or {}).get('preterito', '')
    if isinstance(preterito_desc, str) and preterito_desc.strip().lower().startswith('i '):
        parts = preterito_desc.strip().split(None, 1)
        if len(parts) == 2:
            return parts[1].strip()
    base = _get_english_base(json_data)
    return _derive_simple_past(base)


def _get_spanish_conjugation(json_data: dict, tense: str, person_key: str) -> str:
    """Get Spanish conjugation from indicativo.presente or indicativo.preterito."""
    try:
        indicativo = json_data.get('indicativo', {})
        tense_data = indicativo.get(tense, {})
        return (tense_data.get(person_key, '') or '').strip()
    except (AttributeError, TypeError):
        return ''


def format_english_present_simple(person_index: int, json_data: dict, prefs: dict) -> str:
    """Format English present simple (e.g., 'he knows')."""
    pronoun = ENGLISH_PRONOUNS[person_index]
    base = _get_english_base(json_data)
    if person_index in (2, 3):  # he, it
        verb_form = _get_3rd_person(json_data, prefs)
    else:
        verb_form = base
    return f"{pronoun} {verb_form}"


def format_english_present_progressive(person_index: int, json_data: dict, prefs: dict) -> str:
    """Format English present progressive (e.g., 'he's eating')."""
    gerund = _get_gerund(json_data)
    if not gerund:
        base = _get_english_base(json_data)
        gerund = base + 'ing' if not base.endswith('e') else base[:-1] + 'ing'
    pronoun = ENGLISH_PRONOUNS[person_index]
    if person_index == 0:
        return f"I'm {gerund}"
    if person_index == 1:
        return f"you're {gerund}"
    if person_index in (2, 3):
        return f"he's {gerund}" if person_index == 2 else f"it's {gerund}"
    if person_index == 4:
        return f"we're {gerund}"
    return f"they're {gerund}" if person_index == 5 else f"you guys are {gerund}"


def format_english_present(person_index: int, json_data: dict, prefs: dict) -> str:
    """Format English present - simple or progressive based on es_present_style."""
    style = prefs.get('es_present_style', 'progressive').strip().lower()
    if style == 'simple':
        return format_english_present_simple(person_index, json_data, prefs)
    return format_english_present_progressive(person_index, json_data, prefs)


def format_english_preterite(person_index: int, json_data: dict, prefs: dict) -> str:
    """Format English preterite (e.g., 'I went')."""
    pronoun = ENGLISH_PRONOUNS[person_index]
    verb_form = _get_simple_past(json_data, prefs)
    return f"{pronoun} {verb_form}"


def get_llevar_gerund_subjects(verb: str, count: int = 2) -> List[int]:
    """Return `count` person indices (0-6) deterministically based on verb."""
    rng = random.Random(verb)
    return rng.sample(range(7), count)


def format_english_llevar_gerund(person_index: int, json_data: dict, prefs: dict) -> str:
    """Format English present perfect continuous (e.g., 'I've been doing')."""
    gerund = _get_gerund(json_data)
    if not gerund:
        base = _get_english_base(json_data)
        gerund = base + 'ing' if not base.endswith('e') else base[:-1] + 'ing'
    if person_index == 0:
        return f"I've been {gerund}"
    if person_index == 1:
        return f"you've been {gerund}"
    if person_index in (2, 3):
        return f"he's been {gerund}" if person_index == 2 else f"it's been {gerund}"
    if person_index == 4:
        return f"we've been {gerund}"
    return f"they've been {gerund}" if person_index == 5 else f"you guys have been {gerund}"


def generate_llevar_gerund_cards(
    verb: str,
    json_data: dict,
    prefs: dict,
    llevar_data: dict,
) -> List[Tuple[str, str]]:
    """Generate 2 llevar + gerund flashcards per verb (deterministic subject selection)."""
    subjects = get_llevar_gerund_subjects(verb, 2)
    cards = []
    spanish_gerund = (json_data.get('gerundio', '') or '').strip()
    if not spanish_gerund:
        return cards
    for person_index in subjects:
        spanish_key = SPANISH_PERSON_KEYS[SPANISH_MAP[person_index]]
        llevar_conj = _get_spanish_conjugation(llevar_data, 'presente', spanish_key)
        if not llevar_conj:
            continue
        spanish = f"{llevar_conj} {spanish_gerund}"
        english = format_english_llevar_gerund(person_index, json_data, prefs)
        cards.append((english, spanish))
    return cards


def generate_flashcards_for_verb(json_data: dict, prefs: dict) -> List[Tuple[str, str]]:
    """
    Generate 14 flashcards for a verb (7 present + 7 preterite).
    Spanish conjugations from JSON; English from JSON + prefs.
    """
    flashcards = []

    # Present tense (7 cards)
    for i in range(7):
        spanish_key = SPANISH_PERSON_KEYS[SPANISH_MAP[i]]
        spanish = _get_spanish_conjugation(json_data, 'presente', spanish_key)
        if not spanish:
            continue
        english = format_english_present(i, json_data, prefs)
        flashcards.append((english, spanish))

    # Preterite tense (7 cards)
    for i in range(7):
        spanish_key = SPANISH_PERSON_KEYS[SPANISH_MAP[i]]
        spanish = _get_spanish_conjugation(json_data, 'preterito', spanish_key)
        if not spanish:
            continue
        english = format_english_preterite(i, json_data, prefs)
        flashcards.append((english, spanish))

    return flashcards


def generate_verbs_flashcards(csv_path: str, output_path: str, verbs_dir: str = "verbs") -> None:
    """
    Read verbs.csv (verb, optional WH-choice, optional es_present_style / overrides)
    and generate present+preterite (+ optional llevar) flashcards. Writes to output_path.

    For the full pipeline (config flags, preterite yo/él, questions, IOP), use
    generate_preterite_13_flashcards with verbs_config.txt + verbs.csv.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Verbs CSV file not found: {csv_path}")

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    flashcards = []
    skipped = []

    llevar_data = load_verb_json("llevar", verbs_dir)
    if not llevar_data:
        print("Warning: llevar.json not found; skipping llevar + gerund cards.")

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        names = reader.fieldnames or ()
        if "verb" not in names:
            raise ValueError(f"CSV must have 'verb' column. Found: {list(names)}")

        for row in reader:
            verb = row.get("verb", "").strip()
            if not verb:
                continue

            prefs = {
                "es_present_style": (row.get("es_present_style") or "progressive").strip(),
                "en_3rd_person": (row.get("en_3rd_person") or "").strip(),
                "en_past": (row.get("en_past") or "").strip(),
            }

            json_data = load_verb_json(verb, verbs_dir)
            if json_data is None:
                skipped.append(verb)
                continue

            verb_cards = generate_flashcards_for_verb(json_data, prefs)
            flashcards.extend(verb_cards)

            if llevar_data:
                llevar_cards = generate_llevar_gerund_cards(
                    verb, json_data, prefs, llevar_data
                )
                flashcards.extend(llevar_cards)

    if skipped:
        print(f"Warning: No JSON found for verb(s): {', '.join(skipped)}")

    with open(output_path, "w", encoding="utf-8") as f:
        for english, spanish in flashcards:
            f.write(f"{english}\n{spanish}\n\n")


VALID_FLAGS = frozenset({"preterite-yo", "preterite-el", "llevar", "questions"})


def parse_verbs_config(config_path: str) -> dict:
    """
    Read verbs_config.txt: lines of key: value. Boolean flags use 0/1.
    Also supports iop: 0 | iop: decir,dar
    Empty lines and # comments skipped.
    """
    flags: dict = {}
    if not os.path.exists(config_path):
        return flags

    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" not in stripped:
                continue
            key, val = stripped.split(":", 1)
            key = key.strip()
            val = val.strip()
            if key == "iop":
                if val.lower() in ("0", ""):
                    flags["iop"] = []
                else:
                    flags["iop"] = [v.strip() for v in val.split(",") if v.strip()]
                continue
            if key in VALID_FLAGS and val in ("0", "1"):
                flags[key] = int(val)
    return flags


def load_verb_rows_from_csv(csv_path: str) -> List[Tuple[str, str]]:
    """
    Read verbs.csv: verb column plus optional WH-choice (preterite question drills).
    Returns list of (lemma, wh_fragment) with wh_fragment '' if empty.
    """
    rows: List[Tuple[str, str]] = []
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"verbs CSV not found: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        names = reader.fieldnames or ()
        if "verb" not in names:
            raise ValueError(f"verbs.csv must have 'verb' column. Found: {list(names)}")
        wh_key = "WH-choice" if "WH-choice" in names else (
            "wh-choice" if "wh-choice" in names else None
        )

        for row in reader:
            verb = (row.get("verb") or "").strip()
            if not verb:
                continue
            wh = ""
            if wh_key:
                wh = (row.get(wh_key) or "").strip()
            rows.append((verb, wh))
    return rows


def _wh_fragment_to_english_prefix(wh_sp: str) -> Optional[str]:
    """Map Spanish WH fragment (from CSV) to English question word(s). None if empty."""
    if not wh_sp or not wh_sp.strip():
        return None
    key = wh_sp.strip().lower()
    # Special phrases return full front; caller may adjust word order for some verbs.
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
        "de dónde": "__de_donde__",  # handled in _english_preterite_question_line
    }
    return table.get(key, wh_sp.strip().capitalize())


def _question_subject_pronoun(person_index: int) -> str:
    """Subject pronoun in questions: 'I' stays capitalized; others lowercased."""
    p = ENGLISH_PRONOUNS[person_index]
    if p == "I":
        return "I"
    return p.lower()


def _english_preterite_question_line(
    person_index: int, json_data: dict, wh_sp: str
) -> str:
    """English question matching a Spanish preterite question (7 English personas)."""
    pron = _question_subject_pronoun(person_index)
    es_inf = (json_data.get("infinitivo", "") or "").strip().lower()
    base = _get_english_base(json_data)
    wh_raw = (wh_sp or "").strip().lower()
    wh_en = _wh_fragment_to_english_prefix(wh_sp)

    def was_were_aux(idx: int) -> str:
        # I, you, he, it, we, they, you guys → was/were
        if idx in (1, 4, 5, 6):
            return "were"
        return "was"

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

    if wh_raw == "de qué" or wh_raw == "en qué":
        return f"What did {pron} {base} about?"

    if not wh_en:
        return f"Did {pron} {base}?"

    return f"{wh_en} did {pron} {base}?"


def _spanish_preterite_question(wh_fragment: str, conjugated: str) -> str:
    w = (wh_fragment or "").strip()
    if w:
        return f"¿{w} {conjugated}?"
    return f"¿{conjugated}?"


def generate_question_preterite_flashcards(
    verb_lemma: str,
    wh_choice: str,
    json_data: dict,
) -> List[Tuple[str, str]]:
    """
    Preterite question drills: English question -> Spanish ¿…(WH)… preterite?
    Uses 7 English personas / Spanish persons via SPANISH_MAP.
    Empty WH-choice: yes/no questions only (¿fuiste?).
    """
    cards: List[Tuple[str, str]] = []
    for i in range(7):
        sk = SPANISH_PERSON_KEYS[SPANISH_MAP[i]]
        conj = _get_spanish_conjugation(json_data, "preterito", sk)
        if not conj:
            continue
        en = _english_preterite_question_line(i, json_data, wh_choice)
        if not en:
            continue
        es = _spanish_preterite_question(wh_choice, conj)
        cards.append((en, es))
    return cards


def _parse_verbs_file_with_flags(verbs_path: str) -> Tuple[dict, List[str]]:
    """
    Parse verbs.txt: read optional flags at top (key: 0|1), then verb list.
    Returns (flags_dict, verb_list). Unknown flags ignored.
    Missing preterite-yo / preterite-el default to 1; missing llevar defaults to 0.

    Special: iop: 0 disables. iop: decir or iop: decir,dar lists verbs for IOP
    preterite drills (clitic + conjugated verb). Values are comma-separated.
    """
    flags: dict = {}
    verbs: List[str] = []
    seen = set()
    in_flags = True

    with open(verbs_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                if in_flags:
                    in_flags = False
                continue

            if in_flags and ':' in stripped:
                parts = stripped.split(':', 1)
                key = parts[0].strip()
                val = parts[1].strip()
                if key == "iop":
                    if val.lower() in ("0", ""):
                        flags["iop"] = []
                    else:
                        flags["iop"] = [v.strip() for v in val.split(",") if v.strip()]
                    continue
                if key in VALID_FLAGS and val in ('0', '1'):
                    flags[key] = int(val)
                continue

            in_flags = False
            if stripped not in seen:
                verbs.append(stripped)
                seen.add(stripped)

    return flags, verbs


def generate_iop_preterite_flashcards(
    verb_lemma: str,
    json_data: dict,
) -> List[Tuple[str, str]]:
    """
    English (subject + irregular/simple past + IO object) -> Spanish (IOP clitic + preterite).
    One card per (subject, recipient) with distinct persons (same index excluded).
    """
    english_mid = IOP_VERB_ENGLISH_PRETERITE.get(verb_lemma)
    if not english_mid:
        return []

    cards: List[Tuple[str, str]] = []
    for s in range(len(SPANISH_PERSON_KEYS)):
        for r in range(len(SPANISH_PERSON_KEYS)):
            if s == r:
                continue
            conj = _get_spanish_conjugation(
                json_data, "preterito", SPANISH_PERSON_KEYS[s]
            )
            if not conj:
                continue
            clitic = IOP_SPANISH_CLITICS[r]
            spanish = f"{clitic} {conj}"
            english = (
                f"{IOP_ENGLISH_SUBJECTS[s]} {english_mid} {IOP_ENGLISH_OBJECTS[r]}"
            )
            cards.append((english, spanish))
    return cards


def _get_english_preterite_1st(json_data: dict) -> str:
    """Get English 1st person preterite (e.g. 'I went') from JSON."""
    preterito = (json_data.get('english', {}).get('indicativo', {}) or {}).get('preterito', '')
    if isinstance(preterito, str) and preterito.strip().lower().startswith('i '):
        return preterito.strip()
    # Fallback: build from infinitive
    base = _get_english_base(json_data)
    past = _derive_simple_past(base)
    return f"I {past}" if past else ''


def _english_preterite_1st_to_3rd(english_1st: str) -> str:
    """Convert 'I went' to 'he went'. For reflexives, also shifts possessives: 'my' -> 'his', 'myself' -> 'himself'."""
    s = english_1st.strip()
    if not s.lower().startswith('i '):
        return s
    result = 'he ' + s[2:]
    # Shift 1st-person reflexives/possessives to 3rd person
    result = result.replace(' my ', ' his ')
    result = result.replace(' myself', ' himself')
    return result


def generate_preterite_13_flashcards(
    verbs_path: str = "verbs.txt",
    output_path: str = "data/verbs.txt",
    verbs_dir: str = "verbs",
    config_path: str = "verbs_config.txt",
    csv_path: str = "verbs.csv",
) -> None:
    """
    Build the verbs deck text file.

    Preferred layout:
      - verbs_config.txt — preterite-yo/el, llevar, questions, iop, etc.
      - verbs.csv — verb roster and optional WH-choice for question drills.

    Legacy layout (if config or csv is missing):
      - verbs.txt — same flags at top, then one verb lemma per line.

    Preterite yo/él, llevar + gerund, questions (preterite), and IOP lists follow flags.
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(config_path) and not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"'{config_path}' is present but '{csv_path}' is missing. "
            "Add the CSV roster or remove the config file to use legacy verbs.txt only."
        )

    use_config_csv = os.path.exists(config_path) and os.path.exists(csv_path)
    wh_by_verb: Dict[str, str] = {}

    if use_config_csv:
        flags = parse_verbs_config(config_path)
        verb_rows = load_verb_rows_from_csv(csv_path)
        verbs: List[str] = []
        for v, wh in verb_rows:
            verbs.append(v)
            wh_by_verb[v] = wh
    else:
        if not os.path.exists(verbs_path):
            raise FileNotFoundError(
                f"Verb sources not found: need both '{config_path}' and '{csv_path}', "
                f"or a legacy '{verbs_path}'."
            )
        flags, verbs = _parse_verbs_file_with_flags(verbs_path)
        wh_by_verb = {v: "" for v in verbs}

    gen_yo = flags.get("preterite-yo", 1)
    gen_el = flags.get("preterite-el", 1)
    gen_llevar = flags.get("llevar", 0) == 1
    gen_questions = flags.get("questions", 0) == 1

    llevar_data = None
    if gen_llevar:
        llevar_data = load_verb_json("llevar", verbs_dir)
        if not llevar_data:
            print("Warning: llevar:1 but llevar.json not found; skipping llevar cards.")
            gen_llevar = False

    prefs = {"es_present_style": "progressive"}

    flashcards = []
    skipped_no_json = []
    skipped_preterite = []

    for verb in verbs:
        json_data = load_verb_json(verb, verbs_dir)
        if json_data is None:
            skipped_no_json.append(verb)
            continue

        if gen_yo or gen_el:
            spanish_yo = _get_spanish_conjugation(json_data, 'preterito', 'yo')
            spanish_ud = _get_spanish_conjugation(json_data, 'preterito', 'ud')
            english_1st = _get_english_preterite_1st(json_data)
            english_3rd = _english_preterite_1st_to_3rd(english_1st)

            if not spanish_yo or not spanish_ud or not english_1st:
                skipped_preterite.append(verb)
            else:
                if gen_yo:
                    flashcards.append((english_1st, spanish_yo))
                if gen_el:
                    flashcards.append((english_3rd, f"él {spanish_ud}"))

        if gen_llevar and llevar_data:
            flashcards.extend(
                generate_llevar_gerund_cards(verb, json_data, prefs, llevar_data)
            )

        if gen_questions:
            flashcards.extend(
                generate_question_preterite_flashcards(
                    verb, wh_by_verb.get(verb, ""), json_data
                )
            )

    if skipped_no_json:
        print(f"Warning: No JSON found for verb(s): {', '.join(skipped_no_json)}")
    if skipped_preterite and (gen_yo or gen_el):
        print(
            f"Warning: Missing preterite data for verb(s): {', '.join(skipped_preterite)}"
        )

    iop_verbs = flags.get("iop", [])
    unsupported_iop = []
    for iop_verb in iop_verbs:
        if iop_verb not in IOP_VERB_ENGLISH_PRETERITE:
            unsupported_iop.append(iop_verb)
            continue
        iop_json = load_verb_json(iop_verb, verbs_dir)
        if iop_json is None:
            print(f"Warning: iop list mentions '{iop_verb}' but no JSON found; skipping.")
            continue
        flashcards.extend(generate_iop_preterite_flashcards(iop_verb, iop_json))
    if unsupported_iop:
        print(
            "Warning: IOP preterite not implemented for: "
            f"{', '.join(unsupported_iop)} (add to IOP_VERB_ENGLISH_PRETERITE)"
        )

    with open(output_path, 'w', encoding='utf-8') as f:
        for english, spanish in flashcards:
            f.write(f"{english}\n{spanish}\n\n")
