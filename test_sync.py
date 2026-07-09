"""Tests for deck sync (content TSV <-> progress TSV)."""
import os
import shutil
import tempfile
import unittest

from flashcard import Flashcard
from parser import make_card_id, parse_deck_tsv, write_deck_tsv
from storage import (
    deck_content_path,
    deck_progress_path,
    get_last_session_date,
    load_cards,
    save_cards,
    sync_deck,
)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        os.makedirs("data/decks", exist_ok=True)
        os.makedirs("data/progress", exist_ok=True)

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.temp_dir)

    def _write_content(self, deck_name: str, pairs: list[tuple[str, str]]):
        cards = [
            Flashcard(id=make_card_id(t, d), term=t, definition=d)
            for t, d in pairs
        ]
        write_deck_tsv(deck_content_path(deck_name), cards)

    def test_sync_preserves_progress_on_content_reload(self):
        deck = "test"
        self._write_content(deck, [("hello", "hola"), ("bye", "adios")])

        cards = load_cards(deck_progress_path(deck))
        cards[0].interval = 10
        cards[0].difficulty = 3
        save_cards(cards, deck_progress_path(deck))

        preserved, added, removed = sync_deck(deck)
        self.assertEqual(preserved, 2)
        self.assertEqual(added, 0)
        self.assertEqual(removed, 0)

        reloaded = load_cards(deck_progress_path(deck))
        by_term = {c.term: c for c in reloaded}
        self.assertEqual(by_term["hello"].interval, 10)
        self.assertEqual(by_term["hello"].difficulty, 3)

    def test_sync_adds_new_cards(self):
        deck = "test"
        self._write_content(deck, [("one", "uno")])
        sync_deck(deck)

        self._write_content(deck, [("one", "uno"), ("two", "dos")])
        preserved, added, removed = sync_deck(deck)

        self.assertEqual(preserved, 1)
        self.assertEqual(added, 1)
        self.assertEqual(removed, 0)
        self.assertEqual(len(load_cards(deck_progress_path(deck))), 2)

    def test_sync_removes_deleted_cards(self):
        deck = "test"
        self._write_content(deck, [("one", "uno"), ("two", "dos")])
        sync_deck(deck)

        self._write_content(deck, [("one", "uno")])
        preserved, added, removed = sync_deck(deck)

        self.assertEqual(preserved, 1)
        self.assertEqual(added, 0)
        self.assertEqual(removed, 1)
        self.assertEqual(len(load_cards(deck_progress_path(deck))), 1)

    def test_sync_preserves_last_session_date(self):
        deck = "test"
        self._write_content(deck, [("hello", "hola")])

        path = deck_progress_path(deck)
        cards = load_cards(path)
        save_cards(cards, path)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        lines[0] = "# last_session_date: 2020-01-01\n"
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.writelines(lines)

        sync_deck(deck)
        self.assertEqual(get_last_session_date(path), "2020-01-01")

    def test_sync_content_edit_changes_id(self):
        deck = "test"
        self._write_content(deck, [("old", "viejo")])
        sync_deck(deck)

        cards = load_cards(deck_progress_path(deck))
        cards[0].interval = 7
        save_cards(cards, deck_progress_path(deck))

        self._write_content(deck, [("new", "nuevo")])
        preserved, added, removed = sync_deck(deck)

        self.assertEqual(preserved, 0)
        self.assertEqual(added, 1)
        self.assertEqual(removed, 1)

        reloaded = load_cards(deck_progress_path(deck))
        self.assertEqual(reloaded[0].term, "new")
        self.assertEqual(reloaded[0].interval, 1)

    def test_parse_deck_tsv_one_line_per_card(self):
        deck = "sample"
        path = deck_content_path(deck)
        with open(path, "w", encoding="utf-8") as f:
            f.write("term\tdefinition\n")
            f.write("Roof\tTejado\n")
            f.write("Step aside!\tGolpe avisa!\n")

        cards = parse_deck_tsv(path)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0].term, "Roof")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Deck Sync")
    print("=" * 60)
    unittest.main(verbosity=2)
