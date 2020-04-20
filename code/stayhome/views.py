from django.shortcuts import render
from django.views import generic
from .models import Cards
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
class CardCreateView(generic.TemplateView):
    # FormViewに変更する
    template_name = "input.html"


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
