from django.shortcuts import render
from django.views import generic
from .models import Cards
from django.conf import settings
import boto3


##############
# トップページ #
##############
class TopView(generic.ListView):
    # ListViewに変更する
    template_name = "top.html"
    model = Cards
    context_object_name = "cards"


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
