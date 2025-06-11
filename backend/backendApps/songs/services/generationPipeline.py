from songs.services.songGeneration import generate_songs_with_buffer
from songs.services.songProcessing import prepare_song_list
from constants import GENERATION_BUFFER_MULTIPLIER

def generate_recommendations(user, prompt, count):
    base_prompt = "Jesteś ekspertem muzycznym."
    all_songs, _ = generate_songs_with_buffer(
        prompt, base_prompt, int(count * GENERATION_BUFFER_MULTIPLIER)
    )
    return prepare_song_list(user, all_songs, count)
