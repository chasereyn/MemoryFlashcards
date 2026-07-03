"""Merge data/sources/z_spanish_pass{N}_*.tsv into live decks (append-only, deduped)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from merge_z_spanish import append_cards, build_merge_plan, write_report
from parser import parse_deck_tsv
from storage import sync_deck

SOURCES_DIR = Path("data/sources")


def merge_into(source: Path, deck: Path, report: Path, deck_name: str, apply: bool) -> None:
    if not source.exists():
        raise SystemExit(f"Source not found: {source}")

    incoming = parse_deck_tsv(str(source))
    existing = parse_deck_tsv(str(deck))
    actions = build_merge_plan(incoming, existing)
    to_add = [a for a in actions if a.action in ("add", "disambiguated")]

    write_report(actions, report, applied=False)
    skipped = sum(1 for a in actions if a.action == "skip_exact")
    print(f"{source.name} → {deck.name}")
    print(f"  Source: {len(incoming)} | Append: {len(to_add)} | Skip: {skipped}")

    if apply:
        append_cards(deck, to_add)
        sync_deck(deck_name)
        merged = parse_deck_tsv(str(deck))
        write_report(actions, report, applied=True)
        print(f"  Applied. {deck.name} now has {len(merged)} cards.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge z_spanish pass staging files")
    parser.add_argument("pass_num", type=int, help="Pass number (e.g. 1)")
    parser.add_argument("--apply", action="store_true", help="Append to live decks")
    args = parser.parse_args()

    n = args.pass_num
    merge_into(
        SOURCES_DIR / f"z_spanish_pass{n}_spanish.tsv",
        Path("data/decks/spanish.tsv"),
        Path(f"merge_z_spanish_pass{n}_spanish_report.txt"),
        "spanish",
        args.apply,
    )
    flirt_source = SOURCES_DIR / f"z_spanish_pass{n}_flirt.tsv"
    if flirt_source.exists():
        merge_into(
            flirt_source,
            Path("data/decks/flirt.tsv"),
            Path(f"merge_z_spanish_pass{n}_flirt_report.txt"),
            "flirt",
            args.apply,
        )


if __name__ == "__main__":
    main()
