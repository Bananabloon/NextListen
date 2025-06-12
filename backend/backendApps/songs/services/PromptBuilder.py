import json
from constants import GENERATION_BUFFER_MULTIPLIER
from songs.services.songGeneration import build_preferences_prompt


class PromptBuilder:
    def __init__(self, count, user_preferences, filters=""):
        self.count = count
        self.pref = user_preferences
        self.filters = filters
        self.prefix = build_preferences_prompt(user_preferences)

    def for_song(self, title, artist):
        return f"""
        Podaj {self.count * GENERATION_BUFFER_MULTIPLIER} utworów podobnych do:
        Tytuł: {title}
        Artysta: {artist}
        {self.filters}
        {self.prefix}
        Tylko utwory i artyści, którzy istnieją i są dostępni na Spotify.
        Nie dodawaj komentarzy. Format JSON:
        [{{"title": "tytuł", "artist": "artysta"}}]
        """

    def for_artists(self, artists):
        return f"""
        Podaj {self.count * GENERATION_BUFFER_MULTIPLIER} utworów {self.filters}, inspirowanych twórczością:
        {json.dumps(artists, indent=2)}
        {self.prefix}
        Nie dodawaj komentarzy. Format JSON:
        [{{"title": "tytuł", "artist": "artysta"}}]
        """

    def for_prompt(self, prompt):
        return f"""
        Podaj {self.count * GENERATION_BUFFER_MULTIPLIER} utworów pasujących do opisu:
        "{prompt}"
        {self.prefix}
        Nie dodawaj komentarzy. Format JSON:
        [{{"title": "tytuł", "artist": "artysta"}}]
        """

    def for_top_tracks(self, top_tracks, top_artists):
        return f"""
        Na podstawie ulubionych utworów:
        {json.dumps(top_tracks, indent=2)}

        i ulubionych artystów:
        {json.dumps(top_artists, indent=2)}
        {self.filters}
        {self.prefix}
        Podaj {self.count * GENERATION_BUFFER_MULTIPLIER} rekomendacji.
        Nie dodawaj komentarzy. Format JSON:
        [{{"title": "tytuł", "artist": "artysta"}}]
        """

    def for_discovery(self, artists, tracks, genres):
        genres_str = ", ".join(genres)
        return f"""
        Użytkownik zwykle słucha:
        Artyści: {json.dumps(artists, indent=2, ensure_ascii=False)}
        Utwory: {json.dumps(tracks, indent=2, ensure_ascii=False)}

        Teraz chce poznać nową muzykę z gatunków: {genres_str}
        {self.filters}
        {self.prefix}

        Podaj {self.count * GENERATION_BUFFER_MULTIPLIER} rekomendacji. 
        Nie dodawaj komentarzy. Format JSON:
        [{{"title": "tytuł", "artist": "artysta"}}]
        """

    def for_titles_only(self, titles):
        return f"""
        Podaj {self.count * GENERATION_BUFFER_MULTIPLIER} utworów podobnych do poniższych tytułów:
        {json.dumps(titles, indent=2, ensure_ascii=False)}
        {self.filters}
        {self.prefix}
        Tylko utwory i artyści, którzy istnieją i są dostępni na Spotify.
        Nie dodawaj komentarzy. Format JSON:
        [{{"title": "tytuł", "artist": "artysta"}}]
        """
