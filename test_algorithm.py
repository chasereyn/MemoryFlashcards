"""Test script for spaced repetition algorithm."""
from flashcard import Flashcard
from spaced_repetition import (
    update_card_after_review,
    get_active_cards,
    get_due_cards,
    prioritize_cards,
    get_cards_for_review,
    get_deck_session_info,
    get_today
)


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


def test_daily_limit_caps_due_cards():
    """Test that daily limit caps due cards but always includes active cards."""
    print("Test 6: Daily limit caps due cards")
    today = get_today()

    active = Flashcard(id="active", term="Active", definition="Answer")
    active.first_rating = 1
    active.session_attempts = 1
    active.completed_today = False

    due_cards = [
        Flashcard(id=f"due{i}", term=f"Due {i}", definition="Answer", next_review=today)
        for i in range(50)
    ]
    all_cards = [active] + due_cards

    review = get_cards_for_review(all_cards, today, daily_limit=25)

    assert review[0].id == "active", "Active card should come first"
    assert len(review) == 26, "Should include all active + 25 due cards"
    assert all(c.id != "due49" for c in review), "Cards beyond daily limit should be excluded"
    print("PASSED\n")


def test_deck_session_info():
    """Test today vs backlog counts for deck menu."""
    print("Test 7: Deck session info counts")
    today = get_today()

    due_cards = [
        Flashcard(id=f"due{i}", term=f"Due {i}", definition="Answer", next_review=today)
        for i in range(100)
    ]

    today_count, backlog = get_deck_session_info(due_cards, today, daily_limit=25)

    assert today_count == 25, "Today count should be capped at daily limit"
    assert backlog == 100, "Backlog should reflect all due cards"
    print("PASSED\n")


def test_new_cards_before_old_reviews():
    """Test that new cards are queued before old overdue reviews."""
    print("Test 8: New cards prioritized before old reviews")
    today = get_today()

    old_review = Flashcard(
        id="old", term="Old", definition="Answer",
        next_review="2024-01-01", difficulty=0,
    )
    recent_review = Flashcard(
        id="recent", term="Recent", definition="Answer",
        next_review="2026-07-01", difficulty=0,
    )
    new_card = Flashcard(id="new", term="New", definition="Answer")

    due = prioritize_cards([], [old_review, recent_review, new_card])

    assert due[0].id == "new", "New card should come first"
    assert due[1].id == "recent", "Recently due should beat ancient backlog"
    assert due[2].id == "old", "Oldest overdue should be last"
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
        test_daily_limit_caps_due_cards()
        test_deck_session_info()
        test_new_cards_before_old_reviews()
        
        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"FAILED: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

