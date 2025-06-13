from qdrant_client import QdrantClient

qdrant = QdrantClient(url="http://localhost:6333")
qdrant.delete_collection(collection_name="music_albums_test")
print("Kolekcja została usunięta.")
