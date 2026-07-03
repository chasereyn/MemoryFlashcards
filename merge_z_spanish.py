"""
Merge Z_spanish2000.txt into data/decks/spanish.tsv (append-only).

Usage:
    python merge_z_spanish.py              # dry-run + report
    python merge_z_spanish.py --apply      # append new cards + report
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from flashcard import Flashcard
from parser import make_card_id, parse_deck_tsv, parse_text_file
from storage import sync_deck

Z_SOURCE = Path("Z_spanish2000.txt")
SPANISH_DECK = Path("data/decks/spanish.tsv")
REPORT_PATH = Path("merge_z_spanish_report.txt")

ARTICLES = {"el", "la", "los", "las", "un", "una"}


@dataclass
class MergeAction:
    term: str
    definition: str
    action: str  # add | skip_exact | disambiguated
    note: str = ""


def classify_spanish(definition: str) -> str:
    lower = definition.strip().lower()
    if re.match(r"^(el|la|los|las)(/|\s)", lower) or lower.startswith(
        tuple(f"{a} " for a in ARTICLES)
    ):
        return "noun"
    if re.search(r"\b(se|me|te|nos|os)\b", lower) or lower.endswith("se"):
        return "verb_reflexive"
    if " " not in lower and re.match(r"^[a-záéíóúñü]+(ar|er|ir)$", lower):
        return "verb"
    return "adj_or_other"


def noun_hint(definition: str) -> str:
    parts = definition.strip().split()
    if not parts:
        return "noun"
    first = parts[0].lower().strip("/")
    if first in ARTICLES or first in {"el", "la"}:
        idx = 1
        if parts[0].lower() == "el/la" and len(parts) > 1:
            return parts[1].strip(".,;")
        if first in ARTICLES and len(parts) > 1:
            return parts[1].strip(".,;")
    return "noun"


def spanish_hint(definition: str) -> str:
    d = definition.strip()
    if not d:
        return "alt"
    first = d.split()[0]
    if first.lower() in ARTICLES and len(d.split()) > 1:
        return noun_hint(d)
    return d.split()[0][:24]


def sense_suffix(definition: str) -> str:
    pos = classify_spanish(definition)
    if pos == "noun":
        return f"({noun_hint(definition)})"
    if pos == "verb_reflexive":
        return "(reflexive)"
    if pos == "verb":
        return "(verb)"
    return "(adj)"


def base_term_key(term: str) -> str:
    """Normalize term for collision detection (strip existing disambiguators)."""
    return re.sub(r"\s*\([^)]+\)\s*$", "", term.strip()).lower()


def unique_term(term: str, used_terms: set[str]) -> str:
    candidate = term.strip()
    key = candidate.lower()
    if key not in used_terms:
        used_terms.add(key)
        return candidate

    n = 2
    while True:
        alt = f"{term} ({n})"
        if alt.lower() not in used_terms:
            used_terms.add(alt.lower())
            return alt
        n += 1


def disambiguate_term(base: str, definition: str, used_terms: set[str]) -> str:
    base = base.strip()
    suffix = sense_suffix(definition)
    candidate = f"{base} {suffix}"
    if candidate.lower() not in used_terms:
        used_terms.add(candidate.lower())
        return candidate

    hint = spanish_hint(definition)
    candidate = f"{base} ({hint})"
    return unique_term(candidate, used_terms)


def load_used_terms(cards: list[Flashcard]) -> set[str]:
    return {c.term.lower() for c in cards}


def load_existing_ids(cards: list[Flashcard]) -> set[str]:
    return {c.id for c in cards}


def build_merge_plan(
    z_cards: list[Flashcard], existing: list[Flashcard]
) -> list[MergeAction]:
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
            new_term = disambiguate_term(
                re.sub(r"\s*\([^)]+\)\s*$", "", card.term.strip()),
                card.definition,
                used_terms,
            )
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


def append_cards(path: Path, cards: list[MergeAction]) -> None:
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        for card in cards:
            if card.action in ("add", "disambiguated"):
                writer.writerow([card.term, card.definition])


def write_report(actions: list[MergeAction], path: Path, applied: bool) -> None:
    counts = defaultdict(int)
    for a in actions:
        counts[a.action] += 1

    to_add = [a for a in actions if a.action in ("add", "disambiguated")]
    skipped = [a for a in actions if a.action == "skip_exact"]
    disambiguated = [a for a in actions if a.action == "disambiguated"]

    lines = [
        "merge_z_spanish report",
        f"mode: {'APPLIED' if applied else 'DRY-RUN'}",
        "",
        "=== Summary ===",
        f"Z source cards:        {len(actions)}",
        f"Skipped (exact dup):   {counts['skip_exact']}",
        f"Added (new term):      {counts['add']}",
        f"Added (disambiguated): {counts['disambiguated']}",
        f"Total to append:       {len(to_add)}",
        "",
    ]

    if disambiguated:
        lines.append("=== Disambiguated (first 40) ===")
        for a in disambiguated[:40]:
            lines.append(f"  {a.note}: {a.term}\t{a.definition}")
        if len(disambiguated) > 40:
            lines.append(f"  ... and {len(disambiguated) - 40} more")
        lines.append("")

    if skipped:
        lines.append("=== Skipped exact duplicates (first 30) ===")
        for a in skipped[:30]:
            lines.append(f"  {a.term}\t{a.definition}")
        if len(skipped) > 30:
            lines.append(f"  ... and {len(skipped) - 30} more")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge Z_spanish2000.txt into spanish.tsv")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Append new cards to spanish.tsv (default is dry-run only)",
    )
    args = parser.parse_args()

    if not Z_SOURCE.exists():
        raise SystemExit(f"Source not found: {Z_SOURCE}")

    z_cards = parse_text_file(str(Z_SOURCE))
    existing = parse_deck_tsv(str(SPANISH_DECK))
    actions = build_merge_plan(z_cards, existing)

    to_add = [a for a in actions if a.action in ("add", "disambiguated")]
    write_report(actions, REPORT_PATH, applied=False)

    print(f"Parsed {len(z_cards)} cards from {Z_SOURCE}")
    print(f"Existing spanish.tsv: {len(existing)} cards")
    print(f"Would append: {len(to_add)} cards")
    print(f"Skip exact duplicates: {sum(1 for a in actions if a.action == 'skip_exact')}")
    print(f"Report written to {REPORT_PATH}")

    if args.apply:
        append_cards(SPANISH_DECK, to_add)
        sync_deck("spanish")
        merged = parse_deck_tsv(str(SPANISH_DECK))
        write_report(actions, REPORT_PATH, applied=True)
        print(f"Applied. spanish.tsv now has {len(merged)} cards.")


if __name__ == "__main__":
    main()
