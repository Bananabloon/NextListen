# importQdrant_stream.py

import argparse
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models


def import_collection_streaming(
    input_file: str = "qdrant_export.jsonl",
    collection_name: str = "music_albums_test",
    vector_size: int = 384,
    host: str = "localhost",
    port: int = 6333,
    batch_size: int = 500,
):
    client = QdrantClient(host=host, port=port)

    print(f"Tworzenie kolekcji '{collection_name}' (rozmiar wektora: {vector_size})...")
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size, distance=models.Distance.COSINE
        ),
    )

    buffer = []
    total = 0

    print(f"Importowanie punktów z pliku: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            point = json.loads(line)
            buffer.append(
                models.PointStruct(
                    id=point["id"], vector=point["vector"], payload=point["payload"]
                )
            )

            if len(buffer) >= batch_size:
                client.upsert(collection_name=collection_name, points=buffer)
                total += len(buffer)
                print(f"Wysłano {total} punktów...")
                buffer = []

    if buffer:
        client.upsert(collection_name=collection_name, points=buffer)
        total += len(buffer)
        print(f"Wysłano {total} punktów...")

    print("Import zakończony.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Importuj kolekcję do Qdranta z pliku JSONL."
    )
    parser.add_argument("input_file", help="Plik JSONL z eksportowanymi danymi")
    parser.add_argument("collection", help="Nazwa kolekcji w Qdrant")
    parser.add_argument("vector_size", type=int, help="Rozmiar wektora (np. 384)")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=6333)
    parser.add_argument("--batch", type=int, default=500)

    args = parser.parse_args()

    import_collection_streaming(
        input_file=args.input_file,
        collection_name=args.collection,
        vector_size=args.vector_size,
        host=args.host,
        port=args.port,
        batch_size=args.batch,
    )
