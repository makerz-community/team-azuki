import os
import textwrap
import requests
import boto3
import datetime

from PIL import Image, ImageFont, ImageDraw
from allauth.socialaccount.models import SocialAccount

from django.conf import settings
from ..models import Card

"""""""""""""""""""""""""""""""""""""""""""""""
TODO
- カード全体のデザイン（文字とアイコンの配置、配色とか）
  - とりあえず配置とか大きさとか折り返す文字数とかは適当
- 背景画像
- フォント

Pillowのメモ
Image.new(): ベタ画像作成
ImageDraw.Draw(): Drawオブジェクト作成
ImageDraw.textsize(): 文字列の(length, height)を返す
ImageDraw.text(): 文字列を画像に重ねる
"""""""""""""""""""""""""""""""""""""""""""""""


##############
# 背景画像作成 #
##############
def build_base_image():
    # 背景画像の作成（とりあえずオレンジ。既存画像を使う場合は以下）
    base_image = Image.new("RGB", (1200, 630), (255, 165, 0))

    return base_image


################################
# 画像への文字配置用の関数   （1行） #
################################
def add_text_to_image_oneline(img, text, font_path, font_size, font_color, height, width, max_length=740):
    position = (width, height)
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(img)
    # 文字列がmax_lengthを超える場合は…に置き換え
    if draw.textsize(text, font=font)[0] > max_length:
        while draw.textsize(text + '…', font=font)[0] > max_length:
            text = text[:-1]
        text = text + '…'

    draw.text(position, text, font_color, font=font)
    return img


#######################################
# forループで最後の要素を取得する関数        #
# （add_text_to_image_multilineで使用） #
#######################################
def lastone(iterable):
    """与えられたイテレータブルオブジェクトの
    最後の一つの要素の時にTrue、それ以外の時にFalseを返す
    """
    # イテレータを取得して最初の値を取得する
    it = iter(iterable)
    last = next(it)
    # 2番目の値から開始して反復子を使い果たすまで実行
    for val in it:
        # 一つ前の値を返す
        yield last, False
        last = val  # 値の更新
    # 最後の一つ
    yield last, True


##################################
# 画像への文字配置用の関数（複数行）    #
##################################
def add_text_to_image_multiline(img, text, font_path, font_size, font_color, height, width):
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(img)
    one_line_length = 16
    wrap_list = textwrap.wrap(text, one_line_length)
    line_counter = 0

    # wrap_listから最初の3行を1行づつ取り出し、lineに代入
    # （ただし最後の行だけis_lastがTrueになり、）
    for line, is_last in lastone(wrap_list[:3]):
        # 高さ座標をline_counterに応じて下げる
        y = line_counter * 80 + height
        position = (width, y)

        # 取り出したlineが3行目でかつ、4行目以降が存在する場合は3行目の末尾を「…」にする
        if is_last and wrap_list[3]:
            while len(line) >= one_line_length:
                line = line[:-1]
            line = line + '…'

        draw.multiline_text(position, line, font_color, font=font)  # 1行分の文字列を画像に描画
        line_counter = line_counter + 1  # 行数のカウンターに1
    return img


################################
# 画像へのアイコン貼り付け用の関数定義 #
################################
def add_twitter_icon(img, user):
# def add_twitter_icon(img):
    twitter_account_data = SocialAccount.objects.get(user_id=user.id)
    twitter_icon_url_normal = twitter_account_data.extra_data["profile_image_url_https"]
    # twitter_icon_url_normal = 'https://pbs.twimg.com/profile_images/1221399035887542272/1Mh2IfNL_normal.jpg'

    twitter_icon_url_bigger = twitter_icon_url_normal.replace("_normal", "_bigger")  # サイズが小さいのでbiggerにreplace
    icon = Image.open(io.BytesIO(requests.get(twitter_icon_url_bigger).content))  # TODO マスクかける
    img.paste(icon, (80, 134))

    return img


################################
# S3へのアップロード #
################################
def upload_to_s3(img, card):

    # S3バケットの取得
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

    # S3に保存するパスを設定
    now = datetime.datetime.now()
    file_name = card.auther.username + "_" + now.strftime('%Y%m%d_%H%M%S') + ".png"  # ファイル名
    filepath_db = "test/" + file_name  # db保存用path
    filepath_s3 = "media/" + filepath_db  # S3アップロード用path

    # Imageオブジェクトを一時保存
    file_path_local = "./media/" + file_name
    img.save(file_path_local, "png")

    # boto3にアップロードして、完了したら一時保存したものを削除
    try:
        bucket.upload_file(file_path_local, filepath_s3, ExtraArgs={"ContentType": "image/png"})  # S3に保存
    finally:
        os.remove(file_path_local)  # S3保存処理が終わったらローカルを削除

    # DBのImageFieldを更新
    card.card_image = filepath_db
    card.save()

    # S3のファイルパスを返す
    return card.card_image.url


"""試し（後で削除）"""
base_image = build_base_image()
title = "zoomで飲み会しようようホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲ"
font_path = "./static/fonts/Koruri-Regular.ttf"  # TODO パスの入れ方？ フォント？
font_size = 57
font_color = (255, 255, 255)
height = 100
width = 100
# height = 155
# width = 380

# 1行のテキストを画像に貼る場合
img = add_text_to_image_oneline(base_image, title, font_path, font_size, font_color, height, width)

# 複数行のテキストを画像に貼る場合
img = add_text_to_image_multiline(base_image, title, font_path, font_size, font_color, height, width)

# アイコンを画像に貼る場合
img = add_twitter_icon(base_image)
