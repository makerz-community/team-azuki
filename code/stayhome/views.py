from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic,View
from .forms import CardForm,HashTagsForm
from django.forms.formsets import formset_factory
from .models import Card, HashTags, User
from django.conf import settings
import boto3

from django.contrib import messages
from django.db.models import Q
from functools import reduce
from operator import and_

from .libs.make_card import hashtags_to_one_line,build_base_image,add_text_to_image_oneline,add_text_to_image_multiline,add_twitter_icon,upload_to_s3


##############
# トップページ #
##############
class TopView(generic.ListView):
    template_name = "top.html"
    model = Card
    context_object_name = "cards"


###############
# 募集一覧ページ #
###############
class CardListView(generic.ListView):
    template_name = "cards_list.html"
    model = Card
    context_object_name = "cards"
    # 一回あたりに表示する数は仮置き
    paginate_by = 5

    """ 簡易検索 """

    def get_queryset(self):
        # 検索フォームに値が入力されれば検索を実行
        keyword = self.request.GET.get('keyword')
        if keyword:

            # 募集一覧を取得
            queryset_cards = Card.objects.order_by('-created_at')

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
                [Q(title__icontains=q) | Q(content__icontains=q) |
                 Q(hash_tags__name__icontains=q) for q in q_list]
            )

            # 募集一覧に対して作成したfilterで検索を実行
            queryset = queryset_cards.filter(search_filter)

            # 検索結果とmessages（これは仮）で返す
            messages.info(self.request, '「{}」の検索結果'.format(keyword))
            return queryset

        # 検索フォームに値が入力されなければ普通に一覧全てを返す
        else:
            queryset = Card.objects.order_by('-created_at')
            return queryset


###############
# 募集詳細ページ #
###############
class CardDetailView(generic.DetailView):
    template_name = "cards_detail.html"
    model = Card
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
        bucket.upload_file(filepath_local, filepath_s3, ExtraArgs={
                           "ContentType": "image/png"})  # S3に保存

        return render(request, 'otameshi.html', {'done': "post is done!!!"})


##################
# 募集内容入力ページ #
##################
class CardCreateView(View):
     #formset_factoryを使う
    CardFormSet = formset_factory(CardForm)
    HashTagsFormSet = formset_factory(HashTagsForm,extra=0)

    def get(self,request,*args,**kwargs):
        cards_set = self.CardFormSet(prefix='cards')
        hash_set = self.HashTagsFormSet(prefix='hash')
        context = {
            'cards_set':cards_set,
            'hash_set':hash_set,
        }
        return render(request,'input.html',context)

    def post(self,request,*args,**kwargs):
        # prefixを設定
        cards_set = self.CardFormSet(request.POST,prefix='cards')
        hash_set = self.HashTagsFormSet(request.POST,prefix='hash')

        if cards_set.is_valid() and hash_set.is_valid() :

            # prefixを使うことでcardsのcleaned_dataの中が一段深くなる(複数フォーム想定されるため)
            new_card = Card.objects.create(author=request.user,title=cards_set.cleaned_data[0]['title'],content=cards_set.cleaned_data[0]['content'],
                        conditions=1,meeting_link=cards_set.cleaned_data[0]['meeting_link'],started_at=cards_set.cleaned_data[0]['started_at'],
                        stopped_at=cards_set.cleaned_data[0]['stopped_at'],target_day=cards_set.cleaned_data[0]['target_day'],
                        member_number=cards_set.cleaned_data[0]['member_number'])

            # ハッシュタグを追加したかの確認
            if len(hash_set.cleaned_data) > 0:
                # 空のハッシュタグだけで実質ハッシュタグ無しの場合の対策
                hash_flg = False
                # ハッシュタグは複数入ってくる可能性あるのでfor使う
                for item in hash_set.cleaned_data:

                    # ハッシュタグのフォームの中身が空でない時だけ探す
                    if len(item) > 0:
                        # ハッシュタグが一度でも作られればTrueへ 
                        hash_flg = True

                        # 既にそのハッシュタグ作られていれば作成しない
                        hashtag,complete = HashTags.objects.get_or_create(name=item['hash_tags'])
                        new_card.hash_tags.add(hashtag) 
                    else:
                        continue

                # s3パスが返ってくるはずなのでそれが空でなければ次に進める
                new_card_image_path = card_add_card_image(new_card,request.user,hash_flg)
                
            # ハッシュタグが一つも指定されていない時
            else:
                new_card_image_path = card_add_card_image(new_card,request.user,False)


            # アップロード後のs3パスが0文字でなければ成功とみなしてプレビューページへ
            if len(new_card_image_path) != 0:
                return redirect('extra_app:preview')
            else:
                # エラーなら作った中途半端に作られたカード削除して元のページに返す
                new_card.delete()
                messages.error(request,"画像のアップロードに失敗しました")
                return render(request,'input.html',{'cards_set':cards_set,'hash_set':hash_set})
        else:
            # バリデーションに落ちた時の処理。例：日付フォーマットを間違えた
            return render(request,'input.html',{'cards_set':cards_set,'hash_set':hash_set})



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



################
# マイページ #
#################
class MyPageView(generic.ListView):
    template_name = "mypage.html"
    model = Card
    context_object_name = "cards"
    # mypage.htmlに「cards:自分の募集カード一覧」「user:ログインユーザーの情報」を渡す

    def get_queryset(self):
        return Card.objects.filter(author=self.request.user)

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


# カードを入れるとカードからOGP画像を作って保存までしてくれる関数
# 戻り値にS3のpathを返す。
# hash_flg True->ハッシュタグがある:False->ハッシュタグがない
def card_add_card_image(card,user,hash_flg):
    # """viewsでの呼び出し"""
    # # 1. ベース画像作成とフォント指定
    base_image = build_base_image()
    font_path = "./static/fonts/Koruri-Regular.ttf"
    font_color = (255, 255, 255)

    # # 2. タイトルいれる
    title = card.title
    font_size = 90
    height = 70
    width = 90
    line_height = 105
    one_line_length = 11
    img_with_title = add_text_to_image_multiline(base_image, title, font_path, font_size, font_color, height, width, line_height, one_line_length)

    # # 3. by入れる
    text = "by"
    font_size = 45
    height = 420
    width = 530
    line_height = 100
    one_line_length = 11
    img_with_by = add_text_to_image_oneline(img_with_title, text, font_path, font_size, font_color, height, width)
                
    # # 4. アイコン入れる
    img_with_icon = add_twitter_icon(img_with_by,user)

    # ハッシュタグがあるかどうかで分岐 Trueならハッシュタグがあるとみなす
    if hash_flg:
        # # 5. ハッシュタグ入れる
        tags_list = hashtags_to_one_line(card)
        tags = tags_list
        font_size = 32
        height = 520
        width = 90
        line_height = 40
        one_line_length = 34
        img_complete = add_text_to_image_multiline(img_with_icon, tags, font_path, font_size, font_color, height, width, line_height, one_line_length)

        # # 6. S3にアップロードしてS3のパスを返す
        card_image_path = upload_to_s3(img_complete, card)
    else:
        card_image_path = upload_to_s3(img_with_icon,card)

    return card_image_path