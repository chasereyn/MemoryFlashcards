import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from flashcard import Flashcard


# A card counts as "solid" once its next review is this many days out (Anki's "mature" cutoff)
SOLID_DAYS = 21
HISTORY_PATH = "data/decks/history.json"

BAR_SOLID = "█"
BAR_LEARNING = "▒"
BAR_NEW = "░"


def _use_color() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _paint(text: str, code: str) -> str:
    if not text or not _use_color():
        return text
    return f"\033[{code}m{text}\033[0m"


def green(text: str) -> str:
    return _paint(text, "32")


def yellow(text: str) -> str:
    return _paint(text, "33")


def dim(text: str) -> str:
    return _paint(text, "2")


def bold(text: str) -> str:
    return _paint(text, "1")


def breakdown(cards: List[Flashcard]) -> Tuple[int, int, int]:
    """Split cards into (new, learning, solid) counts.

    new      — never reviewed
    learning — reviewed, but next review is under SOLID_DAYS out
    solid    — next review is SOLID_DAYS or more out
    """
    new = learning = solid = 0
    for card in cards:
        if card.next_review is None and card.first_rating is None:
            new += 1
        elif card.next_review is not None and card.interval >= SOLID_DAYS:
            solid += 1
        else:
            learning += 1
    return new, learning, solid


def deck_bar(new: int, learning: int, solid: int, width: int = 28) -> str:
    """Three-part bar: solid, then learning, then new.

    Any non-zero solid or learning count gets at least one character, so the
    first few cards of a big deck still show up.
    """
    total = new + learning + solid
    if total == 0:
        return dim(BAR_NEW * width)

    solid_w = round(width * solid / total)
    learning_w = round(width * learning / total)
    if solid and solid_w == 0:
        solid_w = 1
    if learning and learning_w == 0:
        learning_w = 1
    solid_w = min(solid_w, width)
    learning_w = min(learning_w, width - solid_w)
    new_w = width - solid_w - learning_w

    return green(BAR_SOLID * solid_w) + yellow(BAR_LEARNING * learning_w) + dim(BAR_NEW * new_w)


def session_bar(done: int, total: int, width: int = 40) -> str:
    """Simple filled bar for progress through one review session."""
    filled = round(width * done / total) if total else width
    return green(BAR_SOLID * filled) + dim(BAR_NEW * (width - filled))


def _load_history() -> dict:
    if not os.path.exists(HISTORY_PATH):
        return {}
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("reviews_by_day", {})
    except Exception:
        return {}


def record_review(today: str) -> None:
    """Count one rating toward today's review total."""
    days = _load_history()
    days[today] = days.get(today, 0) + 1
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump({"reviews_by_day": days}, f, indent=2)
    except Exception as e:
        print(f"Error saving review history: {e}")


def reviews_on(today: str) -> int:
    return _load_history().get(today, 0)


def streak(today: str, days: Optional[dict] = None) -> int:
    """Consecutive days with at least one review, ending today.

    If today has no reviews yet, the streak still counts through yesterday,
    so it does not read as broken before tonight's session.
    """
    if days is None:
        days = _load_history()
    day = datetime.strptime(today, "%Y-%m-%d")
    if not days.get(today):
        day -= timedelta(days=1)
    count = 0
    while days.get(day.strftime("%Y-%m-%d")):
        count += 1
        day -= timedelta(days=1)
    return count
