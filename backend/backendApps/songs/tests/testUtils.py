import pytest
from songs.utils import find_best_match

MOCK_TRACKS = [
    {
        "name": "Digital Love",
        "artists": [{"name": "Daft Punk"}],
        "uri": "spotify:track:123"
    },
    {
        "name": "Teardrop",
        "artists": [{"name": "Massive Attack"}],
        "uri": "spotify:track:456"
    },
    {
        "name": "Paranoid Android",
        "artists": [{"name": "Radiohead"}],
        "uri": "spotify:track:789"
    },
]

def test_exact_match():
    track = find_best_match(MOCK_TRACKS, "Teardrop", "Massive Attack")
    assert track["uri"] == "spotify:track:456"

def test_case_insensitive():
    track = find_best_match(MOCK_TRACKS, "paranoid android", "radiohead")
    assert track["uri"] == "spotify:track:789"

def test_no_match():
    track = find_best_match(MOCK_TRACKS, "Fake Song", "Nonexistent Artist")
    assert track is None