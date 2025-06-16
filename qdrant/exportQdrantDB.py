# exportQdrant.py python exportQdrant.py music_albums_test


import argparse
import json
from qdrant_client import QdrantClient


def export_collection_streaming(
    host: str = "localhost",
    port: int = 6333,
    collection_name: str = "music_albums_test",
    output_file: str = "qdrant_export.json",
    batch_size: int = 1000,
):
    client = QdrantClient(host=host, port=port)
    offset = None
    total_fetched = 0

    print(f"Eksportuję kolekcję '{collection_name}' z Qdranta ({host}:{port})...")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("[\n")
        first = True

        while True:
            response = client.scroll(
                collection_name=collection_name,
                scroll_filter=None,
                limit=batch_size,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )
            points, offset = response
            if not points:
                break

            for point in points:
                if not first:
                    f.write(",\n")
                json.dump(point.dict(), f, ensure_ascii=False)
                first = False

            total_fetched += len(points)
            print(f"Pobrano: {total_fetched} punktów...")

        f.write("\n]\n")

    print(f"Zapisano do pliku: {output_file}")
    print("Eksport zakończony.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Eksportuj kolekcję z Qdranta do JSON."
    )
    parser.add_argument("collection", help="Nazwa kolekcji w Qdrant")
    parser.add_argument(
        "-o",
        "--output",
        default="qdrant_export.json",
        help="Ścieżka do pliku wynikowego",
    )
    parser.add_argument("--host", default="localhost", help="Adres hosta Qdrant")
    parser.add_argument("--port", type=int, default=6333, help="Port Qdranta")
    parser.add_argument(
        "--batch", type=int, default=1000, help="Rozmiar batcha przy pobieraniu"
    )

    args = parser.parse_args()

    export_collection_streaming(
        host=args.host,
        port=args.port,
        collection_name=args.collection,
        output_file=args.output,
        batch_size=args.batch,
    )
