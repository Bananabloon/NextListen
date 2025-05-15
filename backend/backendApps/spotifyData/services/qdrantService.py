import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

client = QdrantClient(host="localhost", port=6333)

FEATURE_KEYS = ["danceability", "energy", "valence", "tempo"]


def _collection_name(genre: str) -> str:
    return f"genre_{genre.lower()}"


def _to_vector(features: dict) -> list[float]:
    return [float(features.get(key, 0.0)) for key in FEATURE_KEYS]


def create_genre_collection(genre: str):
    client.recreate_collection(
        collection_name=_collection_name(genre),
        vectors_config=VectorParams(
            size=len(FEATURE_KEYS),
            distance=Distance.COSINE
        )
    )


def upload_user_preference(user_id: int, genre: str, preferences: dict):
    vector = _to_vector(preferences)
    point = PointStruct(
        id=f"user_{user_id}",
        vector=vector,
        payload={"user_id": user_id}
    )

    client.upsert(
        collection_name=_collection_name(genre),
        points=[point]
    )


def upload_track(track_id: str, genre: str, track_name: str, artist: str, features: dict):
    vector = _to_vector(features)
    point = PointStruct(
        id=f"track_{track_id}",
        vector=vector,
        payload={
            "track_id": track_id,
            "track_name": track_name,
            "artist": artist
        }
    )

    client.upsert(
        collection_name=_collection_name(genre),
        points=[point]
    )


def recommend_tracks_for_user(user_id: int, genre: str, top_k: int = 5):
    collection = _collection_name(genre)
    user_point = client.retrieve(
        collection_name=collection,
        ids=[f"user_{user_id}"],
        with_vectors=True
    )

    if not user_point:
        return []

    user_vector = user_point[0].vector

    results = client.search(
        collection_name=collection,
        query_vector=user_vector,
        limit=top_k,
        filter={
            "must_not": [{"key": "user_id", "match": {"value": user_id}}]
        }
    )

    return results
