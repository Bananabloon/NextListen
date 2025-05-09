from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class Genre(models.Model):
    genreName = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.genreName


class Media(models.Model):
    TYPE_CHOICES = [
        ('song', 'Song'),
        ('album', 'Album'),
    ]


    id = models.AutoField(primary_key=True)
    spotifyMediaURI = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    artistName = models.CharField(max_length=255)
    genreName = models.ForeignKey(Genre, on_delete=models.CASCADE)
    albumName = models.CharField(max_length=255)
    typeOfMedia = models.CharField(max_length=10, choices=TYPE_CHOICES)
    savedAt = models.DateTimeField()

    def __str__(self):
        return self.title


class UserManager(BaseUserManager):
    def create_user(self, spotifyUserId, password=None, **extra_fields):
        if not spotifyUserId:
            raise ValueError("Użytkownik musi mieć ID Spotify")
        user = self.model(spotifyUserId=spotifyUserId, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, spotifyUserId, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(spotifyUserId, password, **extra_fields)
    
    def create_superuser(self, spotifyUserId, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser musi mieć is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser musi mieć is_superuser=True.")

        return self.create_user(spotifyUserId, password, **extra_fields)

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):  
    id = models.AutoField(primary_key=True)
    spotifyUserId = models.CharField(max_length=100, unique=True)
    displayName = models.CharField(max_length=100)
    createdAt = models.DateTimeField(auto_now_add=True)
    lastUpdated = models.DateTimeField(auto_now=True)
    curveballEnjoyment = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = "spotifyUserId"
    REQUIRED_FIELDS = ["displayName"]

    def __str__(self):
        return self.displayName

class PreferenceVector(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    genreName = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True, blank=True)
    preferences = models.JSONField(default=dict)

    def __str__(self):
        return f"Preferences of {self.user.displayName} for {self.genreName}"


class UserFeedback(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    isLiked = models.BooleanField()
    source = models.CharField(max_length=100)
    feedbackAt = models.DateField()

    def __str__(self):
        return f"Feedback by {self.user.displayName} on {self.media.title}"
