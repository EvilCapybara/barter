from django import forms
from .models import ExchangeProposal


class ExchangeProposalForm(forms.ModelForm):

    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender_id', 'ad_receiver_id', 'comment']
        labels = {
            'ad_sender_id': 'Ваше объявление',
            'ad_receiver_id': 'Объявление, на которое хотите обменять',
            'comment': 'Комментарий к обмену',
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

