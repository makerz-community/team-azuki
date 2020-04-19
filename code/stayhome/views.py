from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse,reverse_lazy
from django.views import generic
from .forms import CardCreateForm
from .models import Cards,HashTags,User


##############
# トップページ #
##############
class TopView(generic.TemplateView):
    # ListViewに変更する
    template_name = "top.html"


##################
# 募集内容入力ページ #
##################
class CardCreateView(generic.FormView):
    # FormViewに変更する
    template_name = "input.html"
    form_class = CardCreateForm
    success_url = reverse_lazy('stayhome:preview')

    def form_valid(self,form):
        # ハッシュタグはユニークで保存したいので取得できなかったら作るようにする
        try:
            hashtag = HashTags.objects.get(name=form.cleaned_data['hash_tags'])
        except:
            hashtag = HashTags.objects.create(name=form.cleaned_data['hash_tags'])
        # リクエスト中のユーザーをいれる(twitterとの連携をまた考える)
        author = self.request.user
        # 状態：1>募集中、2>募集終了
        conditions = 1
        # 募集カードを作る
        new_card = Cards.objects.create(author=author,title=form.cleaned_data['title'],content=form.cleaned_data['content'],
        conditions=conditions,meeting_link=form.cleaned_data['meeting_link'],started_at=form.cleaned_data['started_at'],stopped_at=form.cleaned_data['stopped_at'],
        target_day=form.cleaned_data['target_day'],member_number=form.cleaned_data['member_number'])
        # 募集カードにさっき取得(作成)したハッシュタグを加えて保存
        new_card.hash_tags.add(hashtag)
        new_card.save()
        # succes_urlへ
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial["initial_title"] = "募集タイトルを入力してください"
        initial["initial_content"] = "例：エンジニアが集まってワイワイする予定です。お酒飲めない人もたくさん参加するので気軽に応募してください。"
        return initial



############################
# 入力したやつのプレビューページ #
############################
class CardPreviewView(generic.TemplateView):
    template_name = "preview.html"


###############
# シェア用ページ #
###############
class TwitterShareView(generic.TemplateView):
    template_name = "share.html"
