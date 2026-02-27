import csv
import os
from typing import List, Tuple, Optional


def get_verb_type(verb: str) -> str:
    """Determine verb type based on ending: 'ar', 'er', or 'ir'."""
    verb_lower = verb.lower().strip()
    if verb_lower.endswith('ar'):
        return 'ar'
    elif verb_lower.endswith('er'):
        return 'er'
    elif verb_lower.endswith('ir'):
        return 'ir'
    else:
        raise ValueError(f"Unknown verb type for '{verb}'")


def conjugate_spanish_present(verb: str, verb_type: str, provided_conjugations: Optional[List[str]]) -> List[str]:
    """Generate 6 Spanish present tense conjugations."""
    if provided_conjugations and len(provided_conjugations) >= 5:
        conjugations = provided_conjugations[:5]
        conjugations.append(conjugations[4])  # Duplicate ellos for ustedes
        return conjugations
    
    # Standard conjugation rules
    verb_stem = verb[:-2]
    if verb_type == 'ar':
        endings = ['o', 'as', 'a', 'amos', 'an']
    elif verb_type == 'er':
        endings = ['o', 'es', 'e', 'emos', 'en']
    else:  # ir
        endings = ['o', 'es', 'e', 'imos', 'en']
    
    conjugations = [verb_stem + ending for ending in endings]
    conjugations.append(conjugations[4])  # Duplicate ellos for ustedes
    return conjugations


def conjugate_spanish_preterite(verb: str, verb_type: str, provided_conjugations: Optional[List[str]]) -> List[str]:
    """Generate 6 Spanish preterite tense conjugations."""
    if provided_conjugations and len(provided_conjugations) >= 5:
        conjugations = provided_conjugations[:5]
        conjugations.append(conjugations[4])  # Duplicate ellos for ustedes
        return conjugations
    
    # Standard conjugation rules
    verb_stem = verb[:-2]
    if verb_type == 'ar':
        endings = ['é', 'aste', 'ó', 'amos', 'aron']
    else:  # er or ir
        endings = ['í', 'iste', 'ió', 'imos', 'ieron']
    
    conjugations = [verb_stem + ending for ending in endings]
    conjugations.append(conjugations[4])  # Duplicate ellos for ustedes
    return conjugations


def get_gerund_form(verb_data: dict) -> str:
    """Get gerund (-ing) form of verb, using CSV field or auto-generating."""
    # Check if en_gerund is provided in CSV
    en_gerund = verb_data.get('en_gerund', '').strip()
    if en_gerund:
        return en_gerund
    
    # Auto-generate from base verb
    definition = verb_data.get('definition', '').strip()
    base_verb = definition.replace('to ', '').strip() if definition.startswith('to ') else definition.strip()
    
    # Simple rules for generating -ing form
    if base_verb.endswith('e'):
        # Drop final 'e' and add 'ing' (e.g., live -> living)
        return base_verb[:-1] + 'ing'
    else:
        # Just add 'ing' (e.g., eat -> eating, talk -> talking)
        return base_verb + 'ing'


def format_english_present(person_index: int, verb_data: dict) -> str:
    """Format English phrase for present tense using present progressive with contractions."""
    pronouns = ["I", "you", "he", "it", "we", "they", "you guys"]
    pronoun = pronouns[person_index]
    
    gerund = get_gerund_form(verb_data)
    
    # Use contractions for all except "you guys are"
    if person_index == 0:  # I
        return f"I'm {gerund}"
    elif person_index == 1:  # you
        return f"you're {gerund}"
    elif person_index == 2:  # he
        return f"he's {gerund}"
    elif person_index == 3:  # it
        return f"it's {gerund}"
    elif person_index == 4:  # we
        return f"we're {gerund}"
    elif person_index == 5:  # they
        return f"they're {gerund}"
    else:  # you guys (person_index == 6)
        return f"you guys are {gerund}"


def format_english_preterite(person_index: int, verb_data: dict) -> str:
    """Format English phrase for preterite tense."""
    pronouns = ["I", "you", "he", "it", "we", "they", "you guys"]
    pronoun = pronouns[person_index]
    
    en_past = verb_data.get('en_past', '').strip()
    if en_past:
        return f"{pronoun} {en_past}"
    
    # Fallback: add -ed
    definition = verb_data.get('definition', '').strip()
    base_verb = definition.replace('to ', '').strip() if definition.startswith('to ') else definition.strip()
    verb_form = base_verb + 'd' if base_verb.endswith('e') else base_verb + 'ed'
    return f"{pronoun} {verb_form}"


def generate_flashcards_for_verb(verb_data: dict) -> List[Tuple[str, str]]:
    """Generate 14 flashcards for a verb (7 present + 7 preterite)."""
    verb = verb_data.get('verb', '').strip()
    if not verb:
        return []
    
    verb_type = get_verb_type(verb)
    flashcards = []
    
    # Parse Spanish conjugations (space-separated)
    es_present = verb_data.get('es_present', '').strip()
    es_preterite = verb_data.get('es_preterite', '').strip()
    present_list = es_present.split() if es_present else None
    preterite_list = es_preterite.split() if es_preterite else None
    
    # Generate present tense flashcards (7 cards)
    present_conjugations = conjugate_spanish_present(verb, verb_type, present_list)
    # Map: 0=I, 1=you, 2=he, 3=it, 4=we, 5=they, 6=you guys
    # Spanish: 0=yo, 1=tú, 2=él, 3=nosotros, 4=ellos, 5=ustedes
    spanish_map = [0, 1, 2, 2, 3, 4, 4]  # it uses same as he, you guys uses same as they
    for i in range(7):
        spanish_idx = spanish_map[i]
        flashcards.append((format_english_present(i, verb_data), present_conjugations[spanish_idx]))
    
    # Generate preterite tense flashcards (7 cards)
    preterite_conjugations = conjugate_spanish_preterite(verb, verb_type, preterite_list)
    for i in range(7):
        spanish_idx = spanish_map[i]
        flashcards.append((format_english_preterite(i, verb_data), preterite_conjugations[spanish_idx]))
    
    return flashcards


def generate_verbs_flashcards(csv_path: str, output_path: str) -> None:
    """Read verbs.csv and generate flashcards, writing to output_path."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Verbs CSV file not found: {csv_path}")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    flashcards = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validate required columns
        required_columns = ['verb', 'definition']
        if not all(col in reader.fieldnames for col in required_columns):
            raise ValueError(f"CSV missing required columns. Expected: {required_columns}, Found: {reader.fieldnames}")
        
        for row in reader:
            verb = row.get('verb', '').strip()
            definition = row.get('definition', '').strip()
            
            if not verb or not definition:
                continue
            
            verb_data = {
                'verb': verb,
                'definition': definition,
                'en_3rd_person': row.get('en_3rd_person', '').strip(),
                'en_gerund': row.get('en_gerund', '').strip(),
                'en_past': row.get('en_past', '').strip(),
                'es_present': row.get('es_present', '').strip(),
                'es_preterite': row.get('es_preterite', '').strip()
            }
            
            verb_flashcards = generate_flashcards_for_verb(verb_data)
            flashcards.extend(verb_flashcards)
    
    # Write flashcards to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        for english, spanish in flashcards:
            f.write(f"{english}\n{spanish}\n\n")
