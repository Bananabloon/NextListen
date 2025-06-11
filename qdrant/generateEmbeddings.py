from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import json
import numpy as np
import time

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "music_albums_test"
INPUT_FILE = "output.json"

model = SentenceTransformer(MODEL_NAME)
qdrant = QdrantClient(url="http://localhost:6333", timeout=50)


print(f"Tworzę kolekcję '{COLLECTION_NAME}'...")
qdrant.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
)
print("Kolekcja gotowa.\n")


def build_embedding_text(album):
    artist = album["main_artists"][0]
    tracks = [track["title"] for track in album["tracklist"]]

    text = f"""
    Album: {album['album_title']}
    Country: {album['country']}
    Genres: {album['genres']}
    Styles: {album['styles']}
    Artist: {artist['name']}
    Profile: {artist['profile']}
    Tracks: {', '.join(tracks)}
    """
    return text.strip()


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        albums = json.load(f)

    total = len(albums)
    for idx, album in enumerate(albums, start=1):
        text = build_embedding_text(album)

        embedding = model.encode(text)
        embedding_list = embedding.tolist()

        # Logowanie dla podglądu
        print(
            f"[{idx}/{total}] Generuję embedding dla albumu: '{album['album_title']}'"
        )
        print(f"Tekst do embeddingu (skrócony): {text[:100].replace(chr(10), ' ')}...")
        print(f"Embedding (pierwsze 10 wymiarów): {np.array(embedding_list[:10])}")

        metadata = {
            "album_title": album["album_title"],
            "country": album["country"],
            "genres": album["genres"],
            "styles": album["styles"],
            "artist_name": album["main_artists"][0]["name"],
            "artist_profile": album["main_artists"][0]["profile"],
            "tracks": [track["title"] for track in album["tracklist"]],
        }

        vector_id = album["release_id"]

        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=vector_id, vector=embedding_list, payload=metadata
                )
            ],
        )

        time.sleep(0.05)

    print("\nWszystkie embeddingi zostały wygenerowane i wrzucone do Qdranta.")


if __name__ == "__main__":
    main()
