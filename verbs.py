import csv
import json
import os
import random
from typing import List, Tuple, Optional


# Map for 7 English persons: I, you, he, it, we, they, you guys
# Spanish persons: yo, tu, ud, nosotros, uds (Latin American - uds for both they and you guys)
SPANISH_PERSON_KEYS = ['yo', 'tu', 'ud', 'nosotros', 'uds']
ENGLISH_PRONOUNS = ["I", "you", "he", "it", "we", "they", "you guys"]
SPANISH_MAP = [0, 1, 2, 2, 3, 4, 4]  # it=he, you guys=they


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


def _get_english_base(json_data: dict) -> str:
    """Get base verb form from English infinitive (e.g., 'to go' -> 'go')."""
    inf = json_data.get('english', {}).get('infinitivo', '') or json_data.get('infinitivo', '')
    if isinstance(inf, str):
        inf = inf.strip()
        if inf.startswith('to '):
            return inf[3:].strip()
        return inf
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
    Read verbs.csv (settings: verb, es_present_style) and generate flashcards
    from verbs/*.json. Writes to output_path.
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

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if 'verb' not in (reader.fieldnames or []):
            raise ValueError(f"CSV must have 'verb' column. Found: {reader.fieldnames}")

        for row in reader:
            verb = row.get('verb', '').strip()
            if not verb:
                continue

            prefs = {
                'es_present_style': row.get('es_present_style', 'progressive').strip(),
                'en_3rd_person': row.get('en_3rd_person', '').strip(),
                'en_past': row.get('en_past', '').strip(),
            }

            json_data = load_verb_json(verb, verbs_dir)
            if json_data is None:
                skipped.append(verb)
                continue

            verb_cards = generate_flashcards_for_verb(json_data, prefs)
            flashcards.extend(verb_cards)

            if llevar_data:
                llevar_cards = generate_llevar_gerund_cards(verb, json_data, prefs, llevar_data)
                flashcards.extend(llevar_cards)

    if skipped:
        print(f"Warning: No JSON found for verb(s): {', '.join(skipped)}")

    with open(output_path, 'w', encoding='utf-8') as f:
        for english, spanish in flashcards:
            f.write(f"{english}\n{spanish}\n\n")


VALID_FLAGS = frozenset({"preterite-yo", "preterite-el"})


def _parse_verbs_file_with_flags(verbs_path: str) -> Tuple[dict, List[str]]:
    """
    Parse verbs.txt: read optional flags at top (key: 0|1), then verb list.
    Returns (flags_dict, verb_list). Unknown flags ignored. Missing flags default to 1.
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
                if key in VALID_FLAGS and val in ('0', '1'):
                    flags[key] = int(val)
                continue

            in_flags = False
            if stripped not in seen:
                verbs.append(stripped)
                seen.add(stripped)

    return flags, verbs


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
    verbs_path: str,
    output_path: str,
    verbs_dir: str = "verbs",
) -> None:
    """
    Generate preterite 1st/3rd person flashcards from a verb list.
    Cards: English shown -> user answers Spanish.
    Format: 2 cards per verb (I went -> fui, he went -> fue).
    """
    if not os.path.exists(verbs_path):
        raise FileNotFoundError(f"Verbs list not found: {verbs_path}")

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    flags, verbs = _parse_verbs_file_with_flags(verbs_path)
    gen_yo = flags.get("preterite-yo", 1)
    gen_el = flags.get("preterite-el", 1)

    flashcards = []
    skipped = []

    for verb in verbs:
        json_data = load_verb_json(verb, verbs_dir)
        if json_data is None:
            skipped.append(verb)
            continue

        spanish_yo = _get_spanish_conjugation(json_data, 'preterito', 'yo')
        spanish_ud = _get_spanish_conjugation(json_data, 'preterito', 'ud')
        english_1st = _get_english_preterite_1st(json_data)
        english_3rd = _english_preterite_1st_to_3rd(english_1st)

        if not spanish_yo or not spanish_ud or not english_1st:
            skipped.append(verb)
            continue

        if gen_yo:
            flashcards.append((english_1st, spanish_yo))
        if gen_el:
            flashcards.append((english_3rd, f"él {spanish_ud}"))

    if skipped:
        print(f"Warning: No JSON or missing preterite for verb(s): {', '.join(skipped)}")

    with open(output_path, 'w', encoding='utf-8') as f:
        for english, spanish in flashcards:
            f.write(f"{english}\n{spanish}\n\n")
