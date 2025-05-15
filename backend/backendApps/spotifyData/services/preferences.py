from collections import defaultdict
import numpy as np
from users.models import PreferenceVector
from users.serializers import PreferenceVectorSerializer
from .qdrantService import upload_user_preference, create_genre_collection
from qdrant_client.http.exceptions import UnexpectedResponse

FEATURE_KEYS = ["danceability", "energy", "valence", "tempo"]

def extract_genre_vectors(spotify, tracks):
    genre_vectors = defaultdict(list)

    for track in tracks:
        track_id = track["id"]
        artists = track.get("artists", [])
        if not artists:
            continue

        artist_id = artists[0]["id"]
        artist_data = spotify.get_artist(artist_id)
        genres = artist_data.get("genres", ["unknown"])

        audio_features = spotify.get_audio_features(track_id)
        if not audio_features:
            continue

        feature_vector = {
            k: audio_features.get(k, 0.0)
            for k in FEATURE_KEYS
        }

        for genre in genres:
            genre_vectors[genre].append(feature_vector)

    return genre_vectors


def save_preferences(user, genre_vectors):
    result = []

    for genre, vectors in genre_vectors.items():
        if not vectors:
            continue

        averaged = {
            k: float(np.mean([v[k] for v in vectors])) for k in FEATURE_KEYS
        }

        vector_obj, _ = PreferenceVector.objects.update_or_create(
            user=user,
            genreName=genre,
            defaults={"preferences": averaged}
        )

        try:
            create_genre_collection(genre)
        except UnexpectedResponse:
            pass

        upload_user_preference(user.id, genre, averaged)
        result.append(PreferenceVectorSerializer(vector_obj).data)

    return result
