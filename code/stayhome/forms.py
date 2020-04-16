from django import forms
from .models import User,Card,HashTags

class CardCreateForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ('title','context','started_at','stopped_at','target_day','member_number')
