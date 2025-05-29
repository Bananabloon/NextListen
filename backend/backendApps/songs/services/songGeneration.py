import json
from songs.utils import ask_openai, should_send_curveball, extract_filters, find_best_match


def build_preferences_prompt(preferences):
    return f"""
Preferencje użytkownika:
Lubi gatunki: {", ".join(preferences["liked_genres"])}
Lubi artystów: {", ".join(preferences["liked_artists"])}
Nie lubi gatunków: {", ".join(preferences["disliked_genres"])}
Nie lubi artystów: {", ".join(preferences["disliked_artists"])}
Czy użytkownik może dostawać explicit content? - {preferences["explicit_content"]}
"""


def parse_openai_json(content):
    content = content.strip()
    if content.startswith("```") and content.endswith("```"):
        content = "\n".join(content.split("\n")[1:-1])
    return json.loads(content)


def generate_songs_with_buffer(prompt, base_prompt, count, buffer_size=5):
    attempts = 0
    total_count = count + buffer_size

    while attempts < 3:
        raw_response = ask_openai(base_prompt, prompt.replace(f"Podaj {count}", f"Podaj {total_count}"))
        songs = parse_openai_json(raw_response)
        if len(songs) >= count:
            return songs[:count], songs[count:]
        attempts += 1

    return songs[:count], []
