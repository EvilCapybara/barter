from django.db import models
from ads.models import Ad


class ExchangeProposal(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        ACCEPTED = 'accepted', 'Принято'
        REJECTED = 'rejected', 'Отклонено'

    offer_id = models.AutoField(primary_key=True)
    ad_sender_id = models.ForeignKey(to=Ad, on_delete=models.CASCADE, related_name='item_to_give')
    ad_receiver_id = models.ForeignKey(to=Ad, on_delete=models.CASCADE, related_name='item_to_take')
    comment = models.TextField(max_length=255)
    status = models.CharField(choices=StatusChoices.choices, default=StatusChoices.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
