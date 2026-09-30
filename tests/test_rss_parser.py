from types import SimpleNamespace
from unittest.mock import patch

from app.ingestion.rss import (
    fetch_feed,
    generate_fingerprint,
    parse_published_date,
)


def test_parse_published_date():
    entry = SimpleNamespace(
        published_parsed=(
            2026,
            9,
            30,
            12,
            30,
            0,
            2,
            273,
            0,
        )
    )

    result = parse_published_date(entry)

    assert result is not None
    assert result.year == 2026
    assert result.month == 9
    assert result.day == 30
    assert result.hour == 12
    assert result.minute == 30
    assert result.tzinfo is not None


def test_parse_published_date_missing():
    entry = SimpleNamespace(
        published_parsed=None
    )

    result = parse_published_date(entry)

    assert result is None


def test_fingerprint_handles_whitespace():
    first = generate_fingerprint(
        "  NASA Mission  ",
        "  https://example.com/mission  ",
    )

    second = generate_fingerprint(
        "NASA Mission",
        "https://example.com/mission",
    )

    assert first == second
    
def test_fetch_feed_returns_valid_feed():
    fake_feed = SimpleNamespace(
        bozo=False,
        entries=[
            SimpleNamespace(
                title="Test Article",
            )
        ],
    )

    with patch(
        "app.ingestion.rss.feedparser.parse",
        return_value=fake_feed,
    ) as mock_parse:

        result = fetch_feed(
            "https://example.com/feed.xml"
        )

    mock_parse.assert_called_once_with(
        "https://example.com/feed.xml"
    )

    assert result is fake_feed


def test_fetch_feed_raises_on_invalid_empty_feed():
    fake_feed = SimpleNamespace(
        bozo=True,
        entries=[],
    )

    with patch(
        "app.ingestion.rss.feedparser.parse",
        return_value=fake_feed,
    ):

        try:
            fetch_feed(
                "https://example.com/broken.xml"
            )
            assert False, "Expected RuntimeError"
        except RuntimeError as exc:
            assert "Failed to parse RSS feed" in str(exc)