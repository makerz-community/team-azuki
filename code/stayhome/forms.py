from django import forms
from .models import User, Card, HashTags



# 大雑把に属性とか仕込んでみました。labelいつでも使えるように一応残してます。
class CardForm(forms.Form):
    title = forms.CharField(label='募集タイトル', max_length=32,widget=forms.TextInput(attrs={'placeholder':'募集タイトル','class':'form-control'}))
    content = forms.CharField(label='募集内容', max_length=255,widget=forms.Textarea(
        attrs={'placeholder':'(例 若手エンジニアが集まるオンライン飲み会です。\nお酒が苦手な人もたくさんいますのでお気軽にご参加ください。)','class':'form-control'}))
    meeting_link = forms.URLField(
        label='リンク', max_length=255,widget=forms.URLInput(attrs={'placeholder':'ミーティングを行うURLを入れてください','class':'form-control'}))
    started_at = forms.TimeField(label='開始時間',widget=forms.TimeInput(attrs={'placeholder':'開始時間(例 20:00)','class':'form-control'}))
    stopped_at = forms.TimeField(label='終了時間',widget=forms.TimeInput(attrs={'placeholder':'終了時間(例 21:00)','class':'form-control'}))
    target_day = forms.DateField(label='対象日',widget=forms.DateInput(attrs={'placeholder':'対象日(例 2020-04-01)','class':'form-control'}))
    member_number = forms.IntegerField(label='予定人数',widget=forms.NumberInput(attrs={'placeholder':'予定人数','class':'form-control'}))

class HashTagsForm(forms.Form):
    hash_tags = forms.CharField(max_length=255,widget=forms.TextInput(attrs={'placeholder':'ハッシュタグを入力','class':'form-control'}))