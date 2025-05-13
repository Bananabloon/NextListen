from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


class Media(models.Model):
    SONG = 'song'
    ALBUM = 'album'

    TYPE_CHOICES = [
        (SONG, 'Song'),
        (ALBUM, 'Album'),
    ]

    id = models.AutoField(primary_key=True)
    spotify_uri = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    album_name = models.CharField(max_length=255)
    media_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    saved_at = models.DateTimeField()

    def __str__(self):
        return f"{self.title} by {self.artist_name}"


class UserManager(BaseUserManager):
    def create_user(self, spotify_user_id, password=None, **extra_fields):
        if not spotify_user_id:
            raise ValueError("Spotify user ID is required.")
        user = self.model(spotify_user_id=spotify_user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, spotify_user_id, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(spotify_user_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    spotify_user_id = models.CharField(max_length=100, unique=True, db_column='spotifyUserId')
    display_name = models.CharField(max_length=100, db_column='displayName')
    spotify_access_token = models.CharField(max_length=1024, null=True, blank=True)
    spotify_refresh_token = models.CharField(max_length=1024, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    curveball_enjoyment = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    password = models.CharField(max_length=128, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "spotify_user_id"
    REQUIRED_FIELDS = ["display_name"]

    def __str__(self):
        return self.display_name


class PreferenceVector(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True, blank=True)
    preferences = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.display_name}'s preferences for {self.genre}"


class UserFeedback(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    is_liked = models.BooleanField()
    source = models.CharField(max_length=100)
    feedback_at = models.DateField()

    def __str__(self):
        return f"Feedback by {self.user.display_name} on {self.media.title}"
