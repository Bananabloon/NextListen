from users.models import User

def is_curveball(user: User, song_index: int) -> bool:
    interval = max(1, 50 // user.curveball_enjoyment)
    return song_index % interval == 0
