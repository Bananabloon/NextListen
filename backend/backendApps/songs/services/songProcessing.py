from spotifyData.services.spotifyClient import SpotifyAPI
from songs.utils import find_best_match, should_send_curveball
from users.models import UserFeedback, Media
import logging

logger = logging.getLogger(__name__)

def prepare_song_list(user, raw_songs, count):
    spotify = SpotifyAPI(user.spotify_access_token, user.spotify_refresh_token, user)
    prepared = []

    for i, song in enumerate(raw_songs):
        if len(prepared) >= count:
            break

        query = f"{song['title']} {song['artist']}"
        try:
            tracks = spotify.search(query=query, type="track")["tracks"]["items"]
            if not tracks:
                logger.warning(f"[{i}] Brak wyników z Spotify dla: {query}")
                continue

            best_match = find_best_match(tracks, song["title"], song["artist"])
            if not best_match:
                logger.warning(f"[{i}] Brak dopasowania w wynikach Spotify dla: {query}")
                continue

            uri = best_match["uri"]
            track_info = spotify.get_track(best_match["id"])

            try:
                media = Media.objects.get(spotify_uri=uri)
                feedback = UserFeedback.objects.filter(user=user, media=media).first()
                feedback_value = (
                    1 if feedback and feedback.is_liked else
                    -1 if feedback and feedback.is_liked is False else
                    0
                )
            except Media.DoesNotExist:
                feedback_value = 0

            prepared.append({
                "title": song["title"],
                "artist": song["artist"],
                "uri": uri,
                "explicit": best_match["explicit"],
                "curveball": should_send_curveball(user, len(prepared) + 1),
                "feedback_value": feedback_value,
                "track_details": extract_track_details(track_info),
            })
        except Exception as e:
            logger.error(f"[{i}] Błąd przy przetwarzaniu '{query}': {e}")
            continue

    return prepared

def extract_track_details(track_info):
    album_info = track_info.get("album", {})
    return {
        "id": track_info.get("id"),
        "name": track_info.get("name"),
        "artists": [a["name"] for a in track_info.get("artists", [])],
        "album": album_info.get("name"),
        "album_type": album_info.get("album_type"),
        "markets": album_info.get("available_markets"),
        "album_cover": (album_info.get("images", [{}])[0]).get("url"),
        "release_date": album_info.get("release_date"),
        "duration_ms": track_info.get("duration_ms"),
        "popularity": track_info.get("popularity"),
        "preview_url": track_info.get("preview_url"),
        "external_url": track_info.get("external_urls", {}).get("spotify"),
    }

def get_spotify(user):
    return SpotifyAPI(user.spotify_access_token, user.spotify_refresh_token, user)
