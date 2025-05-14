from django.db import models

class AnalyzedSong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    is_curveball = models.BooleanField(default=False)