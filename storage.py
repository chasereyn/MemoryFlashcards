import json
import os
import glob
from datetime import datetime
from typing import List, Optional, Tuple
from flashcard import Flashcard
from parser import parse_text_file


def ensure_data_directory():
    """Create data directory and decks subdirectory if they don't exist."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/decks", exist_ok=True)


def get_deck_name_from_file(filename: str) -> str:
    """Extract deck name from filename (e.g., 'spanish_vocab.txt' -> 'spanish_vocab')."""
    # Remove .txt extension and return
    if filename.endswith('.txt'):
        return filename[:-4]
    return filename


def get_text_files() -> List[str]:
    """Get all .txt files in the data directory."""
    text_files = []
    data_dir = "data"
    
    if os.path.exists(data_dir):
        # Find all .txt files in data/ (not in subdirectories)
        pattern = os.path.join(data_dir, "*.txt")
        text_files = [os.path.basename(f) for f in glob.glob(pattern)]
    
    return text_files


def load_cards(filepath: str) -> List[Flashcard]:
    """
    Load flashcards from JSON file.
    Returns empty list if file doesn't exist.
    """
    if not os.path.exists(filepath):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cards = []
        for card_data in data.get("cards", []):
            cards.append(Flashcard.from_dict(card_data))
        
        return cards
    except Exception as e:
        print(f"Error loading cards from {filepath}: {e}")
        return []


def save_cards(cards: List[Flashcard], filepath: str):
    """Save flashcards to JSON file."""
    ensure_data_directory()
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    data = {
        "cards": [card.to_dict() for card in cards],
        "last_session_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving cards to {filepath}: {e}")


def sync_deck_from_text(text_path: str, deck_name: str) -> Tuple[int, int, int]:
    """
    Sync a deck from text file to JSON file.
    
    Args:
        text_path: Path to the text file
        deck_name: Name of the deck (used for JSON filename)
    
    Returns:
        Tuple of (preserved_count, added_count, removed_count)
    """
    # Parse text file to get cards
    text_cards = parse_text_file(text_path)
    text_ids = {card.id for card in text_cards}
    
    # Load existing JSON cards
    json_path = f"data/decks/{deck_name}.json"
    existing_cards = load_cards(json_path)
    existing_ids = {card.id for card in existing_cards}
    
    # Create a dictionary of existing cards by ID for quick lookup
    existing_dict = {card.id: card for card in existing_cards}
    
    # Build synced cards list
    synced_cards = []
    preserved_count = 0
    added_count = 0
    
    # Keep cards that exist in both (preserve metadata from JSON), in text-file order
    # so new cards are introduced in the order they appear in the deck file
    for text_card in text_cards:
        if text_card.id in existing_dict:
            # Card exists in both - preserve from JSON (has metadata)
            synced_cards.append(existing_dict[text_card.id])
            preserved_count += 1
        else:
            # New card from text file
            synced_cards.append(text_card)
            added_count += 1
    
    # Calculate removed count (cards in JSON but not in text file)
    removed_count = len(existing_ids - text_ids)
    
    # Save synced cards
    save_cards(synced_cards, json_path)
    
    return preserved_count, added_count, removed_count


def sync_all_decks():
    """Sync all text files in data/ with their corresponding JSON files in data/decks/."""
    ensure_data_directory()
    
    text_files = get_text_files()
    
    if not text_files:
        print("No text files found in data/ directory.")
        return
    
    print("\nSyncing decks from text files...")
    
    total_preserved = 0
    total_added = 0
    total_removed = 0
    
    for txt_file in sorted(text_files):
        deck_name = get_deck_name_from_file(txt_file)
        text_path = os.path.join("data", txt_file)
        
        try:
            preserved, added, removed = sync_deck_from_text(text_path, deck_name)

            total_preserved += preserved
            total_added += added
            total_removed += removed
            
        except Exception as e:
            print(f"\nError syncing {deck_name}: {e}")
            continue
    
    print("Sync complete!")
    print(f"Total preserved: {total_preserved} cards")
    print(f"Total added: {total_added} cards")
    print(f"Total removed: {total_removed} cards")


def get_last_session_date(filepath: str) -> Optional[str]:
    """Get the last session date from JSON file."""
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("last_session_date")
    except Exception:
        return None


def text_path_for_deck(json_path: str) -> str:
    """data/decks/spanish.json -> data/spanish.txt"""
    deck_name = os.path.splitext(os.path.basename(json_path))[0]
    return os.path.join("data", f"{deck_name}.txt")


def remove_card_from_text(text_path: str, term: str, definition: str) -> int:
    """Delete every term/definition pair matching this card from a deck file.

    Walks the file with the same pairing rule as parser.py, so a line that
    happens to match the term inside another card is never touched. Both lines
    of the card go together, which keeps every card below it paired correctly.
    Returns the number of pairs removed.
    """
    # newline='' keeps each line's ending exactly as it is on disk, so a delete only
    # touches the card's own lines in the diff
    with open(text_path, 'r', encoding='utf-8', newline='') as f:
        lines = f.readlines()

    drop = set()
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        term_idx = i
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines):
            break
        def_idx = i
        if lines[term_idx].strip() == term and lines[def_idx].strip() == definition:
            drop.update(range(term_idx, def_idx + 1))
            # Take the blank separator after the card with it
            if def_idx + 1 < len(lines) and not lines[def_idx + 1].strip():
                drop.add(def_idx + 1)
        i += 1

    if drop:
        with open(text_path, 'w', encoding='utf-8', newline='') as f:
            f.writelines(line for idx, line in enumerate(lines) if idx not in drop)
    return len([idx for idx in drop if lines[idx].strip()]) // 2


# Lives in the repo root, not data/, so it is never picked up as a deck
FLAGGED_PATH = "flagged.txt"


def flag_card(deck_name: str, term: str, definition: str) -> bool:
    """Add a card to flagged.txt for a later rewrite. Returns False if already flagged."""
    entry = f"{deck_name} | {term} = {definition}\n"
    if os.path.exists(FLAGGED_PATH):
        with open(FLAGGED_PATH, 'r', encoding='utf-8') as f:
            if entry in f.readlines():
                return False
    with open(FLAGGED_PATH, 'a', encoding='utf-8') as f:
        f.write(entry)
    return True
