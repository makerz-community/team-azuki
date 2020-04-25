from django.db import models

CONDITIONS = (
    (1, '募集中'),
    (2, '募集終了'),
)


class User(models.Model):
    username = models.CharField('ユーザー名', max_length=50)
    profile = models.TextField('プロフィール説明', blank=True, null=True)
    twitter_id = models.CharField('TwitterID', max_length=32)
    twitter_oauth_id = models.CharField('Twitter裏id', max_length=255)

    def __str__(self):
        return self.username


class HashTags(models.Model):
    name = models.CharField('タグ名', max_length=32)

    def __str__(self):
        return self.name


class Card(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField('募集タイトル', max_length=32)
    content = models.TextField('募集内容', default='なし')
    meeting_link = models.CharField(
        'リンク', max_length=255, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)
    hash_tags = models.ManyToManyField(HashTags, blank=True)
    conditions = models.IntegerField('状態', choices=CONDITIONS, default=1)
    card_image = models.ImageField('募集画像', blank=True, null=True)
    started_at = models.TimeField('開始時間')
    stopped_at = models.TimeField('終了時間')
    target_day = models.DateField('対象日')
    member_number = models.IntegerField('予定人数', default=1)

    def __str__(self):
        return self.title
