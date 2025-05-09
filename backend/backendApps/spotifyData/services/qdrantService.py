import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

client = QdrantClient(host="localhost", port=6333)

FEATURE_ORDER = ["danceability", "energy", "valence", "tempo"]

def create_genre_collection(genre_name: str):
    client.recreate_collection(
        collection_name=f"genre_{genre_name.lower()}",
        vectors_config=VectorParams(
            size=len(FEATURE_ORDER),
            distance=Distance.COSINE
        )
    )

def feature_dict_to_vector(features: dict) -> list[float]:
    return [float(features.get(key, 0.0)) for key in FEATURE_ORDER]


def upload_user_preference(user_id: int, genre: str, preferences: dict):
    vector = feature_dict_to_vector(preferences)
    client.upsert(
        collection_name=f"genre_{genre.lower()}",
        points=[
            PointStruct(id=f"user_{user_id}", vector=vector, payload={"user_id": user_id})
        ]
    )

def upload_track(track_id: str, genre: str, track_name: str, artist: str, features: dict):
    vector = feature_dict_to_vector(features)
    client.upsert(
        collection_name=f"genre_{genre.lower()}",
        points=[
            PointStruct(
                id=f"track_{track_id}",
                vector=vector,
                payload={
                    "track_id": track_id,
                    "track_name": track_name,
                    "artist": artist
                }
            )
        ]
    )

def recommend_tracks_for_user(user_id: int, genre: str, top_k: int = 5):
    user_point = client.retrieve(
        collection_name=f"genre_{genre.lower()}",
        ids=[f"user_{user_id}"],
        with_vectors=True
    )
    if not user_point:
        return []

    user_vector = user_point[0].vector

    results = client.search(
        collection_name=f"genre_{genre.lower()}",
        query_vector=user_vector,
        limit=top_k,
        filter={"must_not": [{"key": "user_id", "match": {"value": user_id}}]}
    )
    return results
