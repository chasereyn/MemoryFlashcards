"""Merge data/sources/spanishdict_vocab.tsv into spanish.tsv (append-only, deduped)."""
from pathlib import Path

from merge_z_spanish import REPORT_PATH, append_cards, build_merge_plan, write_report
from parser import parse_deck_tsv

SOURCE = Path("data/sources/spanishdict_vocab.tsv")
SPANISH_DECK = Path("data/decks/spanish.tsv")
REPORT = Path("merge_spanishdict_vocab_report.txt")


def main(apply: bool = False) -> None:
    z_cards = parse_deck_tsv(str(SOURCE))
    existing = parse_deck_tsv(str(SPANISH_DECK))
    actions = build_merge_plan(z_cards, existing)
    to_add = [a for a in actions if a.action in ("add", "disambiguated")]

    write_report(actions, REPORT, applied=False)
    print(f"Source: {len(z_cards)} | Would append: {len(to_add)} | Skip: {sum(1 for a in actions if a.action == 'skip_exact')}")

    if apply:
        from storage import sync_deck

        append_cards(SPANISH_DECK, to_add)
        sync_deck("spanish")
        merged = parse_deck_tsv(str(SPANISH_DECK))
        write_report(actions, REPORT, applied=True)
        print(f"Applied. spanish.tsv now has {len(merged)} cards.")


if __name__ == "__main__":
    import sys

    main(apply="--apply" in sys.argv)
