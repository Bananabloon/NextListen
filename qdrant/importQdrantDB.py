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

    print(f"Creating collection '{collection_name}' (vector size: {vector_size})...")
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size, distance=models.Distance.COSINE
        ),
    )

    buffer = []
    total = 0

    print(f"Importing points from file: {input_file}")
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
                print(f"Uploaded {total} points...")
                buffer = []

    if buffer:
        client.upsert(collection_name=collection_name, points=buffer)
        total += len(buffer)
        print(f"Uploaded {total} points...")

    print("Import complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import a collection into Qdrant from a JSONL file."
    )
    parser.add_argument("input_file", help="JSONL file containing exported data")
    parser.add_argument("collection", help="Name of the Qdrant collection")
    parser.add_argument("vector_size", type=int, help="Vector size (e.g., 384)")
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
