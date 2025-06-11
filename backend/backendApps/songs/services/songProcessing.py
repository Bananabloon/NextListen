from spotifyData.services.spotifyClient import SpotifyAPI
from songs.utils import find_best_match, should_send_curveball
from users.models import UserFeedback, Media
import logging

logger = logging.getLogger(__name__)

def prepare_song_list(user, raw_songs, count):
    spotify = SpotifyAPI(user.spotify_access_token, user.spotify_refresh_token, user)
    prepared = []
    track_id_map = {}
    uris = []

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
            if not best_match and tracks:
                logger.warning(f"[{i}] Brak idealnego dopasowania dla '{query}', używam pierwszego wyniku.")
                best_match = tracks[0]

            if "uri" not in best_match:
                continue

            uri = best_match["uri"]
            uris.append(uri)
            track_id_map[uri] = {
                "title": song["title"],
                "artist": song["artist"],
                "explicit": best_match.get("explicit", False),
                "id": best_match["id"],
            }

        except Exception as e:
            logger.error(f"[{i}] Błąd przy wyszukiwaniu '{query}': {e}")
            continue

    track_ids = [meta["id"] for meta in track_id_map.values()]
    track_infos_response = spotify.get_several_tracks(track_ids)

    if isinstance(track_infos_response, dict) and "tracks" in track_infos_response:
        track_infos = track_infos_response["tracks"]
    else:
        track_infos = track_infos_response

    track_info_map = {track["id"]: track for track in track_infos if track is not None}

    for idx, (uri, meta) in enumerate(track_id_map.items()):
        track_info = track_info_map.get(meta["id"])
        if not track_info:
            continue

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
            "uri": uri,
            "explicit": meta["explicit"],
            "curveball": should_send_curveball(user, len(prepared) + 1),
            "feedback_value": feedback_value,
            "track_details": extract_track_details(track_info),
        })

        if len(prepared) >= count:
            break

    return prepared


def extract_track_details(track_info):
    album_info = track_info.get("album", {})
    return {
        "id": track_info.get("id") or "",
        "name": track_info.get("name") or "",
        "artists": [a.get("name", "") for a in track_info.get("artists", [])] if track_info.get("artists") else [],
        "album": album_info.get("name") or "",
        "album_type": album_info.get("album_type") or "",
        "markets": album_info.get("available_markets") or [],
        "album_cover": (album_info.get("images", [{}])[0]).get("url") or "",
        "release_date": album_info.get("release_date") or "",
        "duration_ms": track_info.get("duration_ms") or 0,
        "popularity": track_info.get("popularity") or 0,
        "preview_url": track_info.get("preview_url") or "",
        "external_url": track_info.get("external_urls", {}).get("spotify") or "",
    }


def extract_track_details(track_info):
    album_info = track_info.get("album", {})
    return {
        "id": track_info.get("id") or "",
        "name": track_info.get("name") or "",
        "artists": [a.get("name", "") for a in track_info.get("artists", [])] if track_info.get("artists") else [],
        "album": album_info.get("name") or "",
        "album_type": album_info.get("album_type") or "",
        "markets": album_info.get("available_markets") or [],
        "album_cover": (album_info.get("images", [{}])[0]).get("url") or "",
        "release_date": album_info.get("release_date") or "",
        "duration_ms": track_info.get("duration_ms") or 0,
        "popularity": track_info.get("popularity") or 0,
        "preview_url": track_info.get("preview_url") or "",
        "external_url": track_info.get("external_urls", {}).get("spotify") or "",
    }

def get_spotify(user):
    return SpotifyAPI(user.spotify_access_token, user.spotify_refresh_token, user)