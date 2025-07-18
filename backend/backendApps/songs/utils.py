from users.models import User
from openai import OpenAI
from django.conf import settings
from rapidfuzz import fuzz
import requests
from spotifyData.services.spotifyClient import SpotifyAPI
from constants import SPOTIFY_PLAYLIST_TRACKS_URL, SPOTIFY_PLAYLIST_URL, SPOTIFY_PLAYLIST_ID_URL

GPT_MODEL = "gpt-4o"
GPT_TEMPERATURE = 0.7


def is_curveball(user: User, song_index: int) -> bool:
    interval = max(1, 50 // user.curveball_enjoyment)
    return song_index % interval == 0


def should_send_curveball(user: User, song_index: int) -> bool:
    if user.curveball_enjoyment == 0:
        return False  # ToImplement (ustawianie braku curveballi)
    frequency = max(1, 50 // user.curveball_enjoyment)
    return song_index % frequency == 0


def update_curveball_enjoyment(user: User, liked: bool | None):
    if liked is True and user.curveball_enjoyment < 10:
        user.curveball_enjoyment += 1
    elif liked is False and user.curveball_enjoyment > 1:
        user.curveball_enjoyment -= 1
    user.save()


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def ask_openai(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()},
            ],
            temperature=GPT_TEMPERATURE,
        )
        message_text = response.choices[0].message.content.strip()
        print("### OPENAI RAW RESPONSE ###")
        print(message_text)
        print("###########################")
        if not message_text:
            raise ValueError("OpenAI response is empty")
        return message_text
    except Exception as e:
        print("OpenAI error:", e)
        raise


def extract_filters(request_data):
    filters = []
    mood = request_data.get("mood")
    tempo = request_data.get("tempo")
    style = request_data.get("style")

    if mood:
        filters.append(f"nastroju {mood}")
    if tempo:
        filters.append(f"tempa {tempo}")
    if style:
        filters.append(f"stylu {style}")

    filter_str = ", ".join(filters)
    return f" które pasują do: {filter_str}" if filters else ""


def find_best_match(
    tracks, target_title, target_artist, title_threshold=70, artist_threshold=60
):
    target_title = target_title.lower()
    target_artist = target_artist.lower()

    best_score = 0
    best_match = None

    for track in tracks:
        title = track.get("name", "").lower()
        artists = [a["name"].lower() for a in track.get("artists", [])]
        artist_str = " ".join(artists)

        title_score = fuzz.partial_ratio(target_title, title)
        artist_score = fuzz.partial_ratio(target_artist, artist_str)

        combined_score = (title_score + artist_score) / 2

        if title_score >= title_threshold and artist_score >= artist_threshold:
            if combined_score > best_score:
                best_score = combined_score
                best_match = track

    print(f"TEST - find_best_match zwraca: {best_match}", flush=True)
    return best_match

def create_playlist_with_uris(user, spotify, name, description, uris):
    user_id = spotify.get_user_profile().get("id")
    playlist_payload = {
        "name": name,
        "description": description,
        "public": False
    }

    create_response = requests.post(
        SPOTIFY_PLAYLIST_URL.format(user_id=user_id),
        headers=spotify.headers,
        json=playlist_payload
    )
    if create_response.status_code != 201:
        raise Exception(f"Failed to create playlist: {create_response.status_code} - {create_response.text}")

    playlist_id = create_response.json().get("id")
    for i in range(0, len(uris), 100):
        chunk = uris[i:i + 100]
        add_response = requests.post(
            SPOTIFY_PLAYLIST_TRACKS_URL.format(playlist_id=playlist_id),
            headers=spotify.headers,
            json={"uris": chunk}
        )
        if add_response.status_code != 201:
            raise Exception(f"Failed to add tracks: {add_response.status_code} - {add_response.text}")

    return create_response.json().get("external_urls", {}).get("spotify") or SPOTIFY_PLAYLIST_ID_URL
