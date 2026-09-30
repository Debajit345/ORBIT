from app.ingestion.rss import generate_fingerprint


def test_generate_fingerprint_is_deterministic():
    title = "NASA Announces New Mission"
    url = "https://example.com/nasa-mission"

    first = generate_fingerprint(
        title,
        url,
    )

    second = generate_fingerprint(
        title,
        url,
    )

    assert first == second


def test_generate_fingerprint_is_case_insensitive():
    first = generate_fingerprint(
        "NASA Announces New Mission",
        "https://Example.com/Mission",
    )

    second = generate_fingerprint(
        "nasa announces new mission",
        "https://example.com/mission",
    )

    assert first == second


def test_different_articles_have_different_fingerprints():
    first = generate_fingerprint(
        "NASA Mission A",
        "https://example.com/a",
    )

    second = generate_fingerprint(
        "NASA Mission B",
        "https://example.com/b",
    )

    assert first != second