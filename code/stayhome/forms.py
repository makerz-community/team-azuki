from django import forms
from .models import User, Card, HashTags

from django.forms.formsets import BaseFormSet
from django.core.exceptions import ValidationError



# 予定人数自分入れると確実に1人以上になるので、1人以下ならエラーメッセージを出す
def check_member_number(value):
    if value <= 0:
        raise ValidationError('予定人数は1人以上入力してください。')

# 大雑把に属性とか仕込んでみました。labelいつでも使えるように一応残してます。
class CardForm(forms.Form):
    title = forms.CharField(label='募集タイトル', required=True,min_length=1,max_length=32,error_messages={
        'min_length':'タイトルは1文字以上入れてください。'},widget=forms.TextInput(attrs={'placeholder':'募集タイトル','class':'form-control'}))
    content = forms.CharField(label='募集内容',min_length=1, max_length=255,error_messages={'min_length':'募集内容は1文字以上入れてください'},widget=forms.Textarea(
        attrs={'placeholder':'(例 若手エンジニアが集まるオンライン飲み会です。\nお酒が苦手な人もたくさんいますのでお気軽にご参加ください。)','class':'form-control'}))
    meeting_link = forms.URLField(
        label='リンク',required=False, max_length=255,widget=forms.URLInput(attrs={'placeholder':'ミーティングを行うURLを入れてください','class':'form-control'}))
    started_at = forms.TimeField(label='開始時間',widget=forms.TimeInput(attrs={'placeholder':'開始時間(例 20:00)','class':'form-control'}))
    stopped_at = forms.TimeField(label='終了時間',widget=forms.TimeInput(attrs={'placeholder':'終了時間(例 21:00)','class':'form-control'}))
    target_day = forms.DateField(label='対象日',widget=forms.DateInput(attrs={'placeholder':'対象日(例 2020-04-01)','class':'form-control'}))
    member_number = forms.IntegerField(label='予定人数',validators=[check_member_number],widget=forms.NumberInput(
        attrs={'placeholder':'予定人数','class':'form-control'}))

class HashTagsForm(forms.Form):
    hash_tags = forms.CharField(max_length=255,widget=forms.TextInput(attrs={'placeholder':'ハッシュタグを入力','class':'form-control'}))


class BaseCardFormSet(BaseFormSet):
    def clean(self):
        # 既にフォームの時点で引っかかってたらチェックしない
        if any(self.errors):
            return
        # カードを全フィールド空白にして送信すると、何故かis_valid()に通ってしまうのでフォームセットで対応。(必須項目だけチェック)
        if not self.forms[0].cleaned_data.get('title'):
            self.forms[0].add_error('title','このフィールドは必須です。')
        if not self.forms[0].cleaned_data.get('content'):
            self.forms[0].add_error('content','このフィールドは必須です。')
        if not self.forms[0].cleaned_data.get('started_at'):
            self.forms[0].add_error('started_at','このフィールドは必須です。')
        if not self.forms[0].cleaned_data.get('stopped_at'):
            self.forms[0].add_error('stopped_at','このフィールドは必須です。')
        if not self.forms[0].cleaned_data.get('target_day'):
            self.forms[0].add_error('target_day','このフィールドは必須です。')
        if not self.forms[0].cleaned_data.get('member_number'):
            self.forms[0].add_error('member_number','このフィールドは必須です。')
        