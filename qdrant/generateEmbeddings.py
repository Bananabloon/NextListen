from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import json

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "music_albums_test"
INPUT_FILE = "output.json"
BATCH_SIZE = 500

model = SentenceTransformer(
    MODEL_NAME, device="cuda"
)  # Generation set to GPU, but you need to have PyTorch with CUDA support and CUDA installed
print(f"Using device: {model.device}")

qdrant = QdrantClient(url="http://localhost:6333", timeout=50)

print(f"Creating collection '{COLLECTION_NAME}'...")
qdrant.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
)
print("Collection ready.\n")


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

    print(f"Number of albums to process: {len(albums)}")
    texts = [build_embedding_text(album) for album in albums]

    embeddings = model.encode(
        texts, batch_size=256, device="cuda", show_progress_bar=True
    )

    all_points = []

    for idx, (album, embedding) in enumerate(zip(albums, embeddings), start=1):
        metadata = {
            "genres": list(album.get("genres", [])),
            "styles": list(album.get("styles", [])),
            "artist_name": album["main_artists"][0].get("name", ""),
            "tracks": [track.get("title", "") for track in album.get("tracklist", [])],
        }

        vector_id = album["release_id"]
        point = models.PointStruct(
            id=vector_id, vector=embedding.tolist(), payload=metadata
        )
        all_points.append(point)

        if len(all_points) >= BATCH_SIZE or idx == len(albums):
            qdrant.upsert(collection_name=COLLECTION_NAME, points=all_points)
            print(f"Uploaded {idx}/{len(albums)} points to Qdrant...")
            all_points = []

    print("\nAll embeddings have been generated and saved to Qdrant.")


if __name__ == "__main__":
    main()
