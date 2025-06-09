import pytest
from users.models import User
from songs.utils import (
    is_curveball,
    should_send_curveball,
    update_curveball_enjoyment,
    extract_filters,
    find_best_match,
)

MOCK_TRACKS = [
    {"name": "Digital Love", "artists": [{"name": "Daft Punk"}], "uri": "spotify:track:123"},
    {"name": "Teardrop", "artists": [{"name": "Massive Attack"}], "uri": "spotify:track:456"},
    {"name": "Paranoid Android", "artists": [{"name": "Radiohead"}], "uri": "spotify:track:789"},
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


@pytest.mark.django_db
def test_is_curveball():
    user = User(curveball_enjoyment=5)
    assert is_curveball(user, 10) is True
    assert is_curveball(user, 11) is False

@pytest.mark.django_db
def test_should_send_curveball():
    user = User(curveball_enjoyment=0)
    assert should_send_curveball(user, 1) is False

    user.curveball_enjoyment = 10
    assert should_send_curveball(user, 5) is True

@pytest.mark.django_db
def test_update_curveball_enjoyment_increase():
    user = User(curveball_enjoyment=5)
    update_curveball_enjoyment(user, True)
    assert user.curveball_enjoyment == 6

@pytest.mark.django_db
def test_update_curveball_enjoyment_decrease():
    user = User(curveball_enjoyment=5)
    update_curveball_enjoyment(user, False)
    assert user.curveball_enjoyment == 4

@pytest.mark.django_db
def test_update_curveball_enjoyment_limits():
    user = User(curveball_enjoyment=10)
    update_curveball_enjoyment(user, True)
    assert user.curveball_enjoyment == 10  # max cap

    user.curveball_enjoyment = 1
    update_curveball_enjoyment(user, False)
    assert user.curveball_enjoyment == 1  # min cap

def test_extract_filters():
    data = {"mood": "relaks", "tempo": "wolne", "style": "ambient"}
    result = extract_filters(data)
    assert "relaks" in result and "wolne" in result and "ambient" in result

def test_extract_filters_empty():
    assert extract_filters({}) == ""
