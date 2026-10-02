"""Test script for spaced repetition algorithm."""
import os
from flashcard import Flashcard
from spaced_repetition import (
    update_card_after_review,
    get_active_cards,
    get_due_cards,
    prioritize_cards,
    get_cards_for_review,
    get_today
)
from progress import breakdown, deck_bar, streak, BAR_SOLID, BAR_LEARNING, BAR_NEW


def test_rating_1_keeps_in_session():
    """Test that rating 1 keeps card in session."""
    print("Test 1: Rating 1 keeps card in session")
    card = Flashcard(id="test1", term="Test", definition="Answer")
    
    update_card_after_review(card, 1)
    
    assert card.first_rating == 1, "First rating should be 1"
    assert card.session_attempts == 1, "Session attempts should be 1"
    assert card.completed_today == False, "Card should not be completed"
    assert card.next_review is None, "Next review should not be set yet"
    print("PASSED\n")


def test_rating_1_to_4_updates_metadata():
    """Test that going from 1 to 4 updates metadata based on first rating (1)."""
    print("Test 2: Rating 1 then 4 updates metadata based on first rating")
    card = Flashcard(id="test2", term="Test", definition="Answer", ease_factor=2.5, interval=5)
    
    update_card_after_review(card, 1)
    initial_ease = card.ease_factor
    initial_interval = card.interval
    
    update_card_after_review(card, 4)
    
    assert card.first_rating is None, "Session should be reset"
    assert card.session_attempts == 0, "Session attempts should be reset"
    assert card.completed_today == True, "Card should be completed"
    assert card.ease_factor < initial_ease, "Ease factor should decrease (was difficult)"
    assert card.interval < initial_interval, "Interval should decrease (was difficult)"
    assert card.difficulty > 0, "Struggle count should increase"
    print("PASSED\n")


def test_rating_4_immediate_easy():
    """Test that immediate rating 4 applies exponential backoff."""
    print("Test 3: Immediate rating 4 applies exponential backoff")
    card = Flashcard(id="test3", term="Test", definition="Answer", ease_factor=2.5, interval=5)
    
    # First easy session
    update_card_after_review(card, 4)
    interval_after_first = card.interval
    assert card.consecutive_easy_sessions == 1, "Should have 1 consecutive easy session"
    
    # Reset for next session (simulate new day)
    card.completed_today = False
    card.next_review = get_today()
    
    # Second easy session
    update_card_after_review(card, 4)
    interval_after_second = card.interval
    assert card.consecutive_easy_sessions == 2, "Should have 2 consecutive easy sessions"
    assert interval_after_second > interval_after_first, "Interval should increase with backoff"
    print("PASSED\n")


def test_priority_sorting():
    """Test that cards are prioritized correctly."""
    print("Test 4: Priority sorting")
    
    # Create cards with different states
    active_card = Flashcard(id="active", term="Active", definition="Answer")
    active_card.first_rating = 1
    active_card.session_attempts = 3
    active_card.completed_today = False
    
    due_card = Flashcard(id="due", term="Due", definition="Answer")
    due_card.next_review = get_today()
    due_card.completed_today = True
    
    cards = [due_card, active_card]
    active = get_active_cards(cards)
    due = get_due_cards(cards)
    prioritized = prioritize_cards(active, due)
    
    assert prioritized[0].id == "active", "Active card should come first"
    print("PASSED\n")


def test_multiple_ratings_before_4():
    """Test that multiple 1-3 ratings before 4 all use first rating."""
    print("Test 5: Multiple ratings before 4 use first rating")
    card = Flashcard(id="test5", term="Test", definition="Answer", ease_factor=2.5, interval=5)
    
    update_card_after_review(card, 1)  # First rating: 1
    assert card.first_rating == 1
    
    update_card_after_review(card, 2)  # Second rating: 2
    assert card.first_rating == 1, "First rating should remain 1"
    assert card.session_attempts == 2
    
    update_card_after_review(card, 3)  # Third rating: 3
    assert card.first_rating == 1, "First rating should remain 1"
    assert card.session_attempts == 3
    
    initial_struggle = card.difficulty
    update_card_after_review(card, 4)  # Finally 4
    
    # Should be treated as difficult (based on first rating of 1)
    assert card.difficulty > initial_struggle, "Should increase struggle count"
    assert card.ease_factor < 2.5, "Ease factor should decrease"
    print("PASSED\n")


def test_progress_breakdown():
    """Test new / learning / solid split, including cards left mid-session."""
    print("Test 6: Progress breakdown")
    cards = [
        Flashcard(id="a", term="A", definition="a"),                                   # new
        Flashcard(id="b", term="B", definition="b", first_rating=2),                   # mid-session
        Flashcard(id="c", term="C", definition="c", next_review="2026-10-05", interval=3),
        Flashcard(id="d", term="D", definition="d", next_review="2026-11-01", interval=30),
    ]
    assert breakdown(cards) == (1, 2, 1), f"Got {breakdown(cards)}"
    print("PASSED\n")


def test_deck_bar_shows_small_counts():
    """Test that 1 learning card out of 400 still gets one bar character."""
    print("Test 7: Deck bar keeps small counts visible")
    os.environ["NO_COLOR"] = "1"  # measure characters, not color codes
    bar = deck_bar(399, 1, 0, width=28)
    assert len(bar) == 28, f"Bar should be 28 wide, got {len(bar)}"
    assert bar.count(BAR_LEARNING) == 1, "One learning card should show one character"
    assert deck_bar(0, 0, 10, width=28) == BAR_SOLID * 28, "All-solid deck should be a full bar"
    print("PASSED\n")


def test_streak():
    """Test streak counting, including a day not yet reviewed."""
    print("Test 8: Streak")
    days = {"2026-09-29": 5, "2026-09-30": 3, "2026-10-01": 8}
    assert streak("2026-10-01", days) == 3, "Three days in a row ending today"
    assert streak("2026-10-02", days) == 3, "Unreviewed today should not break the streak yet"
    assert streak("2026-10-03", days) == 0, "A missed day breaks the streak"
    assert streak("2026-10-02", {}) == 0, "No history means no streak"
    print("PASSED\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Spaced Repetition Algorithm")
    print("=" * 60)
    print()
    
    try:
        test_rating_1_keeps_in_session()
        test_rating_1_to_4_updates_metadata()
        test_rating_4_immediate_easy()
        test_priority_sorting()
        test_multiple_ratings_before_4()
        test_progress_breakdown()
        test_deck_bar_shows_small_counts()
        test_streak()
        
        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"FAILED: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

