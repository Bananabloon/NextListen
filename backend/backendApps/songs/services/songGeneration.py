import json
from songs.utils import ask_openai
import re
from users.models import UserFeedback

def build_preferences_prompt(preferences):
    return f"""
    Preferencje użytkownika:
    Lubi gatunki: {", ".join(preferences.get("liked_genres", []))}
    Lubi artystów: {", ".join(preferences.get("liked_artists", []))}
    Nie lubi gatunków: {", ".join(preferences.get("disliked_genres", []))}
    Nie lubi artystów: {", ".join(preferences.get("disliked_artists", []))}
    Czy użytkownik może dostawać explicit content? - {preferences.get("explicit_content", True)}
    """


def parse_openai_json(content: str):
    try:
        match = re.search(r"```json\s*(\[\s*{.*?}\s*\])\s*```", content, re.DOTALL)
        if not match:
            raise ValueError(
                "Nie znaleziono poprawnego formatu JSON w odpowiedzi OpenAI"
            )

        json_str = match.group(1)
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        raise ValueError(f"Błąd dekodowania JSON: {e}")


def generate_songs_with_buffer(
    prompt, base_prompt, count, buffer_size=10
):  # Zwiększono domyślnie do 10
    attempts = 0
    while attempts < 3:
        total_count = count + buffer_size + attempts * 5
        raw_response = ask_openai(
            base_prompt, prompt.replace(f"Podaj {count}", f"Podaj {total_count}")
        )
        songs = parse_openai_json(raw_response)
        if not isinstance(songs, list):
            raise ValueError("OpenAI response is not a list of songs")
        if len(songs) >= count:
            return songs[:count], songs[count:]
        attempts += 1
    return songs[:count], []

def get_user_preferences(user):
    feedbacks = UserFeedback.objects.select_related("media").filter(user=user)
    liked_genres, disliked_genres, liked_artists, disliked_artists = set(), set(), set(), set()

    for feedback in feedbacks:
        if feedback.is_liked:
            liked_genres.update(feedback.media.genre)
            liked_artists.add(feedback.media.artist_name)
        else:
            disliked_genres.update(feedback.media.genre)
            disliked_artists.add(feedback.media.artist_name)

    return {
        "explicit_content": "Tak" if user.explicit_content_enabled else "Nie",
        "liked_genres": list(liked_genres),
        "liked_artists": list(liked_artists),
        "disliked_genres": list(disliked_genres),
        "disliked_artists": list(disliked_artists),
    }