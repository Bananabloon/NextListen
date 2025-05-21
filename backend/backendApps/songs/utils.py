from users.models import User
from openai import OpenAI
from django.conf import settings

GPT_MODEL = "gpt-4o"
GPT_TEMPERATURE = 0.7

def is_curveball(user: User, song_index: int) -> bool:
    interval = max(1, 50 // user.curveball_enjoyment)
    return song_index % interval == 0

def should_send_curveball(user: User, song_index: int) -> bool:
    if user.curveball_enjoyment == 0:
        return False #ToImplement (ustawianie braku curveballi)
    frequency = max(1, 50 // user.curveball_enjoyment)
    return song_index % frequency == 0


def update_curveball_enjoyment(user: User, liked: bool | None):
    if liked is True and user.curveball_enjoyment < 10:
        user.curveball_enjoyment += 1
    elif liked is False and user.curveball_enjoyment > 1:
        user.curveball_enjoyment -= 1
    user.save()


client = OpenAI(api_key=settings.OPENAI_API_KEY)
def ask_openai(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ],
        temperature=GPT_TEMPERATURE
    )
    return response.choices[0].message.content.strip()