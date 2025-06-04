from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, db_index=True, unique=True)
    email = models.CharField(max_length=50, db_index=True)
    bio = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    ad_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username
