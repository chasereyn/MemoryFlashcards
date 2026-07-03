"""
One-time migration: legacy data/*.txt + data/decks/*.json -> TSV format.

Writes data/decks/{name}.tsv (content) and data/progress/{name}.tsv (review metadata).
Skips and removes the F1 deck.

Note: Legacy .txt archives were removed after initial migration. Re-run only if
legacy source files are restored.
"""
import os

import csv
from datetime import datetime

from parser import parse_text_file, write_deck_tsv
from storage import (
    PROGRESS_FIELDNAMES,
    SESSION_DATE_PREFIX,
    deck_content_path,
    deck_progress_path,
    ensure_data_directory,
    load_legacy_json_cards,
)

SKIP_DECKS = {"F1"}


def _write_progress_with_date(cards, deck_name: str, last_session_date: str | None):
    path = deck_progress_path(deck_name)
    session_date = last_session_date or datetime.now().strftime("%Y-%m-%d")

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(f"{SESSION_DATE_PREFIX}{session_date}\n")
        writer = csv.DictWriter(f, fieldnames=PROGRESS_FIELDNAMES, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for card in cards:
            writer.writerow({
                "id": card.id,
                "next_review": card.next_review or "",
                "ease_factor": card.ease_factor,
                "interval": card.interval,
                "difficulty": card.difficulty,
                "completed_today": "true" if card.completed_today else "false",
                "first_rating": card.first_rating if card.first_rating is not None else "",
                "session_attempts": card.session_attempts,
                "consecutive_easy_sessions": card.consecutive_easy_sessions,
                "latest_rating": card.latest_rating if card.latest_rating is not None else "",
            })


def convert_deck(txt_path: str, deck_name: str) -> None:
    content_cards = parse_text_file(txt_path)
    json_path = f"data/decks/{deck_name}.json"
    json_cards, last_session_date = load_legacy_json_cards(json_path)

    json_by_id = {c.id: c for c in json_cards}

    merged = []
    for card in content_cards:
        if card.id in json_by_id:
            saved = json_by_id[card.id]
            card.next_review = saved.next_review
            card.ease_factor = saved.ease_factor
            card.interval = saved.interval
            card.difficulty = saved.difficulty
            card.completed_today = saved.completed_today
            card.first_rating = saved.first_rating
            card.session_attempts = saved.session_attempts
            card.consecutive_easy_sessions = saved.consecutive_easy_sessions
            card.latest_rating = saved.latest_rating
        merged.append(card)

    write_deck_tsv(deck_content_path(deck_name), content_cards)
    _write_progress_with_date(merged, deck_name, last_session_date)
    print(f"  {deck_name}: {len(content_cards)} cards")


def main():
    ensure_data_directory()

    txt_files = sorted(f for f in os.listdir("data") if f.endswith(".txt"))
    if not txt_files:
        print("No legacy .txt files in data/ to convert.")
        return

    print("Converting legacy decks to TSV...")
    for txt_file in txt_files:
        deck_name = txt_file[:-4]
        if deck_name in SKIP_DECKS:
            continue
        convert_deck(os.path.join("data", txt_file), deck_name)

    print("Done.")


if __name__ == "__main__":
    main()
