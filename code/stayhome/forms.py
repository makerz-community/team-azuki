from django import forms
from .models import User, Cards, HashTags


# ModelForm使わずにFormでhash_tagsも一緒にとるように変えました
class CardCreateForm(forms.Form):
    title = forms.CharField(label='募集タイトル', max_length=32,widget=forms.TextInput)
    content = forms.CharField(label='募集内容', max_length=255,widget=forms.Textarea)
    meeting_link = forms.CharField(
        label='リンク', max_length=255,widget=forms.TextInput)
    started_at = forms.TimeField(label='開始時間',widget=forms.TextInput)
    stopped_at = forms.TimeField(label='終了時間',widget=forms.TextInput)
    target_day = forms.DateField(label='対象日',widget=forms.DateInput)
    member_number = forms.IntegerField(label='予定人数',widget=forms.NumberInput)
    hash_tags = forms.CharField(label='ハッシュタグ',max_length=255,widget=forms.TextInput)