import pandas as pd
import json


def nan_to_none(value):
    return None if pd.isna(value) else value


df = pd.read_csv("output.csv")

albums = []
for release_id, group in df.groupby("release_id"):
    first = group.iloc[0]
    genres = list(set(str(first["genres"]).strip("{}").replace('"', "").split(",")))
    genres = [g.strip() for g in genres if g.strip()]
    styles = list(set(str(first["styles"]).strip("{}").replace('"', "").split(",")))
    styles = [s.strip() for s in styles if s.strip()]

    main_artists = []
    for _, row in group[["artist_name", "artist_profile"]].drop_duplicates().iterrows():
        main_artists.append(
            {
                "name": nan_to_none(row["artist_name"]),
                "profile": nan_to_none(row["artist_profile"]),
            }
        )

    tracklist = []
    for _, row in (
        group[["track_position", "track_title"]]
        .dropna(subset=["track_position"])
        .iterrows()
    ):
        tracklist.append(
            {
                "position": nan_to_none(row["track_position"]),
                "title": nan_to_none(row["track_title"]),
            }
        )

    album = {
        "release_id": nan_to_none(release_id),
        "album_title": nan_to_none(first["album_title"]),
        "country": nan_to_none(first["country"]),
        "released": nan_to_none(first["released"]),
        "genres": genres,
        "styles": styles,
        "main_artists": main_artists,
        "tracklist": tracklist,
    }
    albums.append(album)

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(albums, f, ensure_ascii=False, indent=2)
