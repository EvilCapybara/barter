from django.db import models
from users.models import User


class Ad(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/у'),
    ]

    class ConditionChoices(models.TextChoices):
        NEW = 'new', 'Новый'
        USED = 'used', 'Б/у'

    item_id = models.AutoField(primary_key=True)  # для переопределения имени поля
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=100)
    condition = models.CharField(choices=ConditionChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='ads')

    def __str__(self):
        return self.title
