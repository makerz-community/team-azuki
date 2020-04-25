from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse,reverse_lazy
from django.views import generic
from .forms import CardCreateForm
from .models import Cards,HashTags,User
from django.conf import settings
import boto3

from django.contrib import messages
from django.db.models import Q
from functools import reduce
from operator import and_


##############
# トップページ #
##############
class TopView(generic.ListView):
    template_name = "top.html"
    model = Cards
    context_object_name = "cards"


###############
# 募集一覧ページ #
###############
class CardListView(generic.ListView):
    template_name = "cards_list.html"
    model = Cards
    context_object_name = "cards"
    # 一回あたりに表示する数は仮置き
    paginate_by = 5

    """ 簡易検索 """
    def get_queryset(self):
        # 検索フォームに値が入力されれば検索を実行
        keyword = self.request.GET.get('keyword')
        if keyword:

            # 募集一覧を取得
            queryset_cards = Cards.objects.order_by('-created_at')

            # 複数ワード検索する用に、キーワードからスペースを取り除いて文字列を作成
            exclusion = {' ', '　'}
            q_list = ''
            for i in keyword:
                if i in exclusion:
                    pass
                else:
                    q_list += i

            # Qオブジェクトで検索用のfilterを作成
            search_filter = reduce(
                and_,
                [Q(title__icontains=q) | Q(content__icontains=q) | Q(hash_tags__name__icontains=q) for q in q_list]
            )

            # 募集一覧に対して作成したfilterで検索を実行
            queryset = queryset_cards.filter(search_filter)

            # 検索結果とmessages（これは仮）で返す
            messages.info(self.request, '「{}」の検索結果'.format(keyword))
            return queryset

        # 検索フォームに値が入力されなければ普通に一覧全てを返す
        else:
            queryset = Cards.objects.order_by('-created_at')
            return queryset


###############
# 募集詳細ページ #
###############
class CardDetailView(generic.DetailView):
    template_name = "cards_detail.html"
    model = Cards
    context_object_name = "card"


#####################
# 試しページ（後で削除） #
#####################
class OtameshiView(generic.TemplateView):
    template_name = "otameshi.html"

    def post(self, request, *args, **kwargs):
        # バケットの取得
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        # ローカルのファイルとS3のパスを取得（パスの書き方はあとで検討）
        filepath_local = "./media/fff_test.png"
        filepath_s3 = "media/test/fff_test.png"

        # bucket.upload_file('アップロードするするローカルファイルのpath', '保存先S3のpath')
        bucket.upload_file(filepath_local, filepath_s3, ExtraArgs={"ContentType": "image/png"})  # S3に保存

        return render(request, 'otameshi.html', {'done': "post is done!!!"})


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
