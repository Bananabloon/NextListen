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
    print(f"Connecting to Qdrant at {host}:{port}...")
    client = QdrantClient(host=host, port=port)

    offset = None
    total_fetched = 0
    print(f"Exporting collection '{collection_name}' to file '{output_file}'...")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("[")
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
                        f.write(",")
                    json.dump(
                        point.dict(), f, ensure_ascii=False, separators=(",", ":")
                    )
                    first = False

                total_fetched += len(points)
                print(f"Fetched: {total_fetched} points...")

            f.write("]")

        print(f"Export completed ({total_fetched} points)")
        print(f"File saved: {output_file}")

    except Exception as e:
        print(f"Error during export: {e}")


if __name__ == "__main__":
    print(">>> Qdrant export script started")

    parser = argparse.ArgumentParser(description="Export a Qdrant collection to JSON.")
    parser.add_argument("collection", help="Name of the collection in Qdrant")
    parser.add_argument(
        "-o", "--output", default="qdrant_export.json", help="Path to the output file"
    )
    parser.add_argument("--host", default="localhost", help="Qdrant host address")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant port")
    parser.add_argument(
        "--batch", type=int, default=1000, help="Batch size for fetching data"
    )

    args = parser.parse_args()

    export_collection_streaming(
        host=args.host,
        port=args.port,
        collection_name=args.collection,
        output_file=args.output,
        batch_size=args.batch,
    )
