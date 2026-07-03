"""
Merge Z_spanish_phrases1000.txt into data/decks/spanish.tsv (append-only).

Usage:
    python merge_z_phrases.py              # dry-run + report
    python merge_z_phrases.py --apply      # append new cards + report
"""
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

from flashcard import Flashcard
from parser import make_card_id, parse_deck_tsv
from storage import sync_deck

from merge_z_spanish import (
    MergeAction,
    append_cards,
    base_term_key,
    build_merge_plan,
    disambiguate_term,
    load_existing_ids,
    load_used_terms,
    sense_suffix,
    unique_term,
)

Z_SOURCE = Path("Z_spanish_phrases1000.txt")
SPANISH_DECK = Path("data/decks/spanish.tsv")
REPORT_PATH = Path("merge_z_phrases_report.txt")

MOJIBAKE_REPLACEMENTS = [
    ("ΓÇÖ", "'"),
    ("ΓÇ£", '"'),
    ("ΓÇ¥", '"'),
    ("ΓÇö", "—"),
    ("ΓÇô", "–"),
    ("┬┐", "¿"),
    ("┬í", "¡"),
    ("├⌐", "é"),
    ("├®", "é"),
    ("├¡", "í"),
    ("├│", "ó"),
    ("├║", "ú"),
    ("├▒", "ñ"),
    ("├í", "á"),
    ("├ü", "Á"),
    ("├ë", "É"),
    ("├ì", "Í"),
    ("├ô", "Ó"),
    ("├Ü", "Ú"),
    ("├æ", "Ñ"),
]

MOJIBAKE_MARKERS = re.compile(r"[┬├Γ]")


def fix_mojibake(text: str) -> str:
    text = text.replace("\ufeff", "")
    if not MOJIBAKE_MARKERS.search(text):
        return text
    for bad, good in MOJIBAKE_REPLACEMENTS:
        text = text.replace(bad, good)
    return text


def parse_phrases_file(filepath: Path) -> tuple[list[Flashcard], int]:
    """Parse two-line phrase file; skip # comments; repair encoding."""
    lines = filepath.read_text(encoding="utf-8").splitlines()
    cleaned: list[str] = []
    encoding_fixes = 0

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fixed = fix_mojibake(stripped)
        if fixed != stripped.replace("\ufeff", ""):
            encoding_fixes += 1
        cleaned.append(fixed)

    flashcards: list[Flashcard] = []
    seen_ids: set[str] = set()
    i = 0
    while i + 1 < len(cleaned):
        term = cleaned[i]
        definition = cleaned[i + 1]
        card_id = make_card_id(term, definition)
        if card_id not in seen_ids:
            seen_ids.add(card_id)
            flashcards.append(Flashcard(id=card_id, term=term, definition=definition))
        i += 2

    if len(cleaned) % 2:
        raise ValueError(f"Odd number of content lines after cleanup ({len(cleaned)}) — orphan tail")

    return flashcards, encoding_fixes


def phrase_sense_suffix(term: str, definition: str) -> str:
    lower = definition.lower()
    if re.search(r"\b(estás|eres|tienes|puedes|haces|vas|te |contigo|tú)\b", lower):
        return "(tú)"
    if re.search(r"\b(usted|tenga|podría|puede ayudarme|le gusta|su refri|me puede)\b", lower):
        return "(formal)"
    if "!" in term and "sneeze" not in term.lower() and "bendiga" in lower:
        return "(sneeze)"
    return sense_suffix(definition)


def build_phrase_merge_plan(
    z_cards: list[Flashcard], existing: list[Flashcard]
) -> list[MergeAction]:
    """Like build_merge_plan but uses phrase-aware disambiguation."""
    existing_ids = load_existing_ids(existing)
    used_terms = load_used_terms(existing)
    existing_by_base = defaultdict(list)
    for card in existing:
        existing_by_base[base_term_key(card.term)].append(card)

    actions: list[MergeAction] = []

    for card in z_cards:
        if card.id in existing_ids:
            actions.append(
                MergeAction(card.term, card.definition, "skip_exact", "already in spanish.tsv")
            )
            continue

        base = base_term_key(card.term)
        collides = base in existing_by_base or card.term.lower() in used_terms

        if collides:
            stripped = re.sub(r"\s*\([^)]+\)\s*$", "", card.term.strip())
            suffix = phrase_sense_suffix(stripped, card.definition)
            candidate = f"{stripped} {suffix}"
            if candidate.lower() not in used_terms:
                used_terms.add(candidate.lower())
                new_term = candidate
            else:
                new_term = disambiguate_term(stripped, card.definition, used_terms)
            actions.append(
                MergeAction(
                    new_term,
                    card.definition,
                    "disambiguated",
                    f"was {card.term!r}",
                )
            )
        else:
            new_term = unique_term(card.term.strip(), used_terms)
            actions.append(MergeAction(new_term, card.definition, "add", ""))

    return actions


def write_report(
    actions: list[MergeAction],
    path: Path,
    applied: bool,
    encoding_fixes: int,
    source_count: int,
) -> None:
    counts = defaultdict(int)
    for action in actions:
        counts[action.action] += 1

    to_add = [a for a in actions if a.action in ("add", "disambiguated")]
    skipped = [a for a in actions if a.action == "skip_exact"]
    disambiguated = [a for a in actions if a.action == "disambiguated"]

    lines = [
        "merge_z_phrases report",
        f"mode: {'APPLIED' if applied else 'DRY-RUN'}",
        "",
        "=== Summary ===",
        f"Z source cards:        {source_count}",
        f"Encoding fixes:        {encoding_fixes}",
        f"Skipped (exact dup):   {counts['skip_exact']}",
        f"Added (new term):      {counts['add']}",
        f"Added (disambiguated): {counts['disambiguated']}",
        f"Total to append:       {len(to_add)}",
        "",
    ]

    if disambiguated:
        lines.append("=== Disambiguated (first 40) ===")
        for action in disambiguated[:40]:
            lines.append(f"  {action.note}: {action.term}\t{action.definition}")
        if len(disambiguated) > 40:
            lines.append(f"  ... and {len(disambiguated) - 40} more")
        lines.append("")

    if skipped:
        lines.append("=== Skipped exact duplicates ===")
        for action in skipped:
            lines.append(f"  {action.term}\t{action.definition}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge Z_spanish_phrases1000.txt into spanish.tsv"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Append new cards to spanish.tsv (default is dry-run only)",
    )
    args = parser.parse_args()

    if not Z_SOURCE.exists():
        raise SystemExit(f"Source not found: {Z_SOURCE}")

    z_cards, encoding_fixes = parse_phrases_file(Z_SOURCE)
    existing = parse_deck_tsv(str(SPANISH_DECK))
    actions = build_phrase_merge_plan(z_cards, existing)

    to_add = [a for a in actions if a.action in ("add", "disambiguated")]
    write_report(actions, REPORT_PATH, applied=False, encoding_fixes=encoding_fixes, source_count=len(z_cards))

    print(f"Parsed {len(z_cards)} cards from {Z_SOURCE}")
    print(f"Encoding fixes applied: {encoding_fixes}")
    print(f"Existing spanish.tsv: {len(existing)} cards")
    print(f"Would append: {len(to_add)} cards")
    print(f"Skip exact duplicates: {sum(1 for a in actions if a.action == 'skip_exact')}")
    print(f"Report written to {REPORT_PATH}")

    if args.apply:
        append_cards(SPANISH_DECK, to_add)
        sync_deck("spanish")
        merged = parse_deck_tsv(str(SPANISH_DECK))
        write_report(
            actions, REPORT_PATH, applied=True, encoding_fixes=encoding_fixes, source_count=len(z_cards)
        )
        print(f"Applied. spanish.tsv now has {len(merged)} cards.")


if __name__ == "__main__":
    main()
