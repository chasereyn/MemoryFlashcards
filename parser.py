import csv
import hashlib
from typing import List

from flashcard import Flashcard

DECK_FIELDNAMES = ["term", "definition"]


def make_card_id(term: str, definition: str) -> str:
    """Stable id from term + definition (matches legacy JSON ids)."""
    id_string = f"{term}|{definition}"
    return hashlib.md5(id_string.encode("utf-8")).hexdigest()[:12]


def parse_deck_tsv(filepath: str) -> List[Flashcard]:
    """
    Parse a deck TSV file: one card per line (term, definition).
    Optional header row starting with 'term'.
    """
    flashcards = []
    seen_ids = set()

    try:
        with open(filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if not row or all(not cell.strip() for cell in row):
                    continue
                if row[0].strip().lower() == "term":
                    continue
                if len(row) < 2:
                    continue

                term = row[0].strip()
                definition = row[1].strip()
                if not term or not definition:
                    continue

                card_id = make_card_id(term, definition)
                if card_id in seen_ids:
                    continue
                seen_ids.add(card_id)

                flashcards.append(
                    Flashcard(id=card_id, term=term, definition=definition)
                )
    except FileNotFoundError:
        print(f"Warning: {filepath} not found.")
        return []
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return []

    return flashcards


def parse_text_file(filepath: str) -> List[Flashcard]:
    """
    Parse legacy two-line text format (term, definition, blank line between cards).
    Used by convert_decks.py only.
    """
    flashcards = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]

        i = 0
        while i < len(lines):
            if not lines[i]:
                i += 1
                continue

            term = lines[i]
            i += 1

            while i < len(lines) and not lines[i]:
                i += 1

            if i < len(lines):
                definition = lines[i]
                card_id = make_card_id(term, definition)

                if not any(card.id == card_id for card in flashcards):
                    flashcards.append(
                        Flashcard(id=card_id, term=term, definition=definition)
                    )
                i += 1
    except FileNotFoundError:
        print(f"Warning: {filepath} not found.")
        return []
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return []

    return flashcards


def write_deck_tsv(filepath: str, cards: List[Flashcard]) -> None:
    """Write deck content to TSV (term, definition only)."""
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(DECK_FIELDNAMES)
        for card in cards:
            writer.writerow([card.term, card.definition])
