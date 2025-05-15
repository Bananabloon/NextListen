from users.models import User

def is_curveball(user: User, song_index: int) -> bool:
    interval = max(1, 50 // user.curveball_enjoyment)
    return song_index % interval == 0

def should_send_curveball(user: User, song_index: int) -> bool:
    if user.curveball_enjoyment == 0:
        return False #ToImplement
    frequency = max(1, 50 // user.curveball_enjoyment)
    return song_index % frequency == 0


def update_curveball_enjoyment(user: User, liked: bool | None):
    if liked is True and user.curveball_enjoyment < 10:
        user.curveball_enjoyment += 1
    elif liked is False and user.curveball_enjoyment > 1:
        user.curveball_enjoyment -= 1
    user.save()
