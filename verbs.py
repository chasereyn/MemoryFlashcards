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
    """
    Generate 6 Spanish present tense conjugations.
    Returns: [yo, tú, él, nosotros, ellos, ellos] (last two are same for ustedes)
    """
    verb_stem = verb[:-2]  # Remove 'ar', 'er', or 'ir'
    
    if provided_conjugations and len(provided_conjugations) >= 5:
        # Use provided conjugations (expects 5 forms)
        conjugations = provided_conjugations[:5]  # Take first 5
        conjugations.append(conjugations[4])  # Duplicate ellos for ustedes
        return conjugations
    
    # Fallback to standard conjugation rules
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
    """
    Generate 6 Spanish preterite tense conjugations.
    Returns: [yo, tú, él, nosotros, ellos, ellos] (last two are same for ustedes)
    """
    verb_stem = verb[:-2]  # Remove 'ar', 'er', or 'ir'
    
    if provided_conjugations and len(provided_conjugations) >= 5:
        # Use provided conjugations (expects 5 forms)
        conjugations = provided_conjugations[:5]  # Take first 5
        conjugations.append(conjugations[4])  # Duplicate ellos for ustedes
        return conjugations
    
    # Fallback to standard conjugation rules
    if verb_type == 'ar':
        endings = ['é', 'aste', 'ó', 'amos', 'aron']
    elif verb_type == 'er':
        endings = ['í', 'iste', 'ió', 'imos', 'ieron']
    else:  # ir
        endings = ['í', 'iste', 'ió', 'imos', 'ieron']
    
    conjugations = [verb_stem + ending for ending in endings]
    conjugations.append(conjugations[4])  # Duplicate ellos for ustedes
    return conjugations


def format_english_present(person_index: int, verb_data: dict) -> str:
    """
    Format English phrase for present tense.
    person_index: 0=I, 1=you, 2=he, 3=we, 4=they, 5=you guys
    """
    pronouns = ["I", "you", "he", "we", "they", "you guys"]
    pronoun = pronouns[person_index]
    
    definition = verb_data.get('definition', '').strip()
    en_3rd_person = verb_data.get('en_3rd_person', '').strip()
    
    # Remove "to " prefix if present
    base_verb = definition.replace('to ', '').strip() if definition.startswith('to ') else definition.strip()
    
    if person_index == 2:  # 3rd person singular (he)
        if en_3rd_person:
            return f"{pronoun} {en_3rd_person}"
        else:
            # Add 's' to base verb for 3rd person singular
            verb_form = base_verb + 's' if base_verb else ''
            return f"{pronoun} {verb_form}"
    else:
        # All other persons use base form
        return f"{pronoun} {base_verb}"


def format_english_preterite(person_index: int, verb_data: dict) -> str:
    """
    Format English phrase for preterite tense.
    person_index: 0=I, 1=you, 2=he, 3=we, 4=they, 5=you guys
    """
    pronouns = ["I", "you", "he", "we", "they", "you guys"]
    pronoun = pronouns[person_index]
    
    definition = verb_data.get('definition', '').strip()
    en_past_tense = verb_data.get('en_past_tense', '').strip()
    
    if en_past_tense:
        # Use provided past tense for all persons
        return f"{pronoun} {en_past_tense}"
    else:
        # Remove "to " prefix and add "ed" (or "d" if verb ends in "e")
        base_verb = definition.replace('to ', '').strip() if definition.startswith('to ') else definition.strip()
        if base_verb.endswith('e'):
            verb_form = base_verb + 'd'
        else:
            verb_form = base_verb + 'ed' if base_verb else ''
        return f"{pronoun} {verb_form}"


def parse_verb_row(row: dict) -> dict:
    """Parse a TSV row into structured verb data."""
    verb_data = {
        'verb': row.get('verb', '').strip(),
        'definition': row.get('definition', '').strip(),
        'en_3rd_person': row.get('en_3rd_person', '').strip(),
        'en_past_tense': row.get('en_past_tense', '').strip(),
        'es_present': row.get('es_present', '').strip(),
        'es_preterite': row.get('es_preterite', '').strip()
    }
    
    # Parse Spanish conjugations (space-separated)
    if verb_data['es_present']:
        verb_data['es_present_list'] = verb_data['es_present'].split()
    else:
        verb_data['es_present_list'] = None
    
    if verb_data['es_preterite']:
        verb_data['es_preterite_list'] = verb_data['es_preterite'].split()
    else:
        verb_data['es_preterite_list'] = None
    
    return verb_data


def generate_flashcards_for_verb(verb_data: dict) -> List[Tuple[str, str]]:
    """
    Generate 12 flashcards for a verb (6 present + 6 preterite).
    Returns list of tuples: (english_phrase, spanish_conjugation)
    """
    verb = verb_data['verb']
    if not verb:
        return []
    
    verb_type = get_verb_type(verb)
    flashcards = []
    
    # Spanish subject pronouns
    spanish_pronouns = ["yo", "tú", "él", "nosotros", "ellos", "ustedes"]
    
    # Generate present tense flashcards (6 cards)
    present_conjugations = conjugate_spanish_present(
        verb, 
        verb_type, 
        verb_data.get('es_present_list')
    )
    
    for i in range(6):
        english = format_english_present(i, verb_data)
        spanish = f"{spanish_pronouns[i]} {present_conjugations[i]}"
        flashcards.append((english, spanish))
    
    # Generate preterite tense flashcards (6 cards)
    preterite_conjugations = conjugate_spanish_preterite(
        verb,
        verb_type,
        verb_data.get('es_preterite_list')
    )
    
    for i in range(6):
        english = format_english_preterite(i, verb_data)
        spanish = f"{spanish_pronouns[i]} {preterite_conjugations[i]}"
        flashcards.append((english, spanish))
    
    return flashcards


def generate_verbs_flashcards(tsv_path: str, output_path: str) -> None:
    """
    Read verbs.tsv and generate flashcards, writing to output_path.
    Exits with error if TSV is malformed.
    """
    if not os.path.exists(tsv_path):
        raise FileNotFoundError(f"Verbs TSV file not found: {tsv_path}")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    flashcards = []
    
    try:
        with open(tsv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            # Validate required columns
            required_columns = ['verb', 'definition']
            if not all(col in reader.fieldnames for col in required_columns):
                raise ValueError(f"TSV missing required columns. Expected: {required_columns}, Found: {reader.fieldnames}")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                verb_data = parse_verb_row(row)
                
                # Skip rows without verb or definition
                if not verb_data['verb'] or not verb_data['definition']:
                    continue
                
                verb_flashcards = generate_flashcards_for_verb(verb_data)
                flashcards.extend(verb_flashcards)
    
    except csv.Error as e:
        raise ValueError(f"Error parsing TSV file at line {row_num}: {e}")
    except Exception as e:
        raise ValueError(f"Error processing verbs TSV: {e}")
    
    # Write flashcards to output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for english, spanish in flashcards:
                f.write(f"{english}\n")
                f.write(f"{spanish}\n")
                f.write("\n")
    except Exception as e:
        raise IOError(f"Error writing to output file {output_path}: {e}")
