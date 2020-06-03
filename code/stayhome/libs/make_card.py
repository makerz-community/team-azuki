import io
import os
import textwrap
import requests
import boto3
import datetime

from PIL import Image, ImageFont, ImageDraw, ImageFilter
from allauth.socialaccount.models import SocialAccount

from django.conf import settings
from ..models import Card

"""""""""""""""""""""""""""""""""""""""""""""""
Pillowのメモ
Image.new(): ベタ画像作成
ImageDraw.Draw(): Drawオブジェクト作成
ImageDraw.textsize(): 文字列の(length, height)を返す
ImageDraw.text(): 文字列を画像に重ねる
"""""""""""""""""""""""""""""""""""""""""""""""


#######################################
# forループで最後の要素を取得する関数        #
# （add_text_to_image_multilineで使用） #
#######################################
def lastone(iterable):
    """
    与えられたイテレータブルオブジェクトの
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


#############################
# ハッシュタグ取得して整形する関数 #
#############################
def hashtags_to_one_line(card):
    # カードに紐づいているハッシュタグを取得する
    hashtags_names = list(card.hash_tags.all().values_list("name", flat=True))

    # 画像に描画するように「#ハッシュタグ1 #ハッシュタグ2 ...」の形式に整形する
    names_list_with_hash = list(map(lambda x: "#" + x, hashtags_names))  # ['#ハッシュタグ1', '#ハッシュタグ2', '#ハッシュタグ3',...]
    one_line_hashtags = " ".join(names_list_with_hash)

    return one_line_hashtags


##############
# 背景画像作成 #
##############
def build_base_image():
    # 背景画像の作成（オレンジ）
    base_image = Image.new("RGB", (1200, 630), (255, 165, 0))

    return base_image


################################
# 画像への文字配置用の関数（1行）    #
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


##################################
# 画像への文字配置用の関数（複数行）    #
##################################
def add_text_to_image_multiline(img, text, font_path, font_size, font_color, height, width, line_height, one_line_length):
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(img)
    wrap_list = textwrap.wrap(text, one_line_length)
    line_counter = 0

    # wrap_listが3行以上になるとき
    if len(wrap_list) > 3:
        # wrap_listから最初の3行を1行づつ取り出し、lineに代入
        # （ただし最後の行だけis_lastがTrueになり、末尾を「…」に置換）
        for line, is_last in lastone(wrap_list[:3]):
            # 高さ座標をline_counter(行数)に応じて下げる
            y = line_counter * line_height + height
            position = (width, y)
            # 取り出したlineが3行目の場合は末尾を「…」に置換する
            if is_last:
                while len(line) >= one_line_length:
                    line = line[:-1]
                line = line + '…'
            draw.multiline_text(position, line, font_color, font=font)  # 1行分の文字列を画像に描画
            line_counter = line_counter + 1  # 行数のカウンターに1

    # wrap_listが3行未満になるとき
    else:
        for line in wrap_list:
            # 高さ座標をline_counterに応じて下げる
            y = line_counter * line_height + height
            position = (width, y)
            draw.multiline_text(position, line, font_color, font=font)  # 1行分の文字列を画像に描画
            line_counter = line_counter + 1  # 行数のカウンターに1

    return img


#######################
# アイコン貼り付け用の関数 #
#######################
def add_twitter_icon(img, user):
    twitter_account_data = SocialAccount.objects.get(user_id=user.id)
    twitter_icon_url_normal = twitter_account_data.extra_data["profile_image_url_https"]

    twitter_icon_url_bigger = twitter_icon_url_normal.replace("_normal", "_bigger")  # サイズが小さいのでbiggerにreplace
    icon = Image.open(io.BytesIO(requests.get(twitter_icon_url_bigger).content))

    # 円形のマスク作成
    mask = Image.new("L", icon.size)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, icon.size[0], icon.size[1]), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1))
    del draw
    icon.putalpha(mask)

    # openしただけではメモリに載ってるだけなので、処理した内容は処理終了後メモリの内容が消えると同時に消えちゃうので一時保存してすぐ削除する
    icon.save("./media/sample.png")
    img.paste(icon, (600, 420), icon)
    del icon

    return img


###################
# S3へのアップロード #
###################
def upload_to_s3(img, card):

    # S3バケットの取得
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

    # S3に保存するパスを設定
    now = datetime.datetime.now()
    file_name = card.author.username + "_" + now.strftime('%Y%m%d_%H%M%S') + ".png"  # ファイル名
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


# """viewsでの呼び出し"""
# # 1. ベース画像作成とフォント指定
# base_image = build_base_image()
# font_path = "./static/fonts/Koruri-Regular.ttf"
# font_color = (255, 255, 255)
#
# # 2. タイトルいれる
# title = card.title
# font_size = 90
# height = 70
# width = 90
# line_height = 105
# one_line_length = 11
# img_with_title = add_text_to_image_multiline(base_image, title, font_path, font_size, font_color, height, width, line_height, one_line_length)
#
# # 3. by入れる
# text = "by"
# font_size = 45
# height = 420
# width = 530
# line_height = 100
# one_line_length = 11
# img_with_by = add_text_to_image_oneline(img_with_title, text, font_path, font_size, font_color, height, width)
#
# # 4. アイコン入れる
# img_with_icon = add_twitter_icon(img_with_by)
#
# # 5. ハッシュタグ入れる
# tags_list = hashtags_to_one_line(card)
# tags = tags_list
# font_size = 32
# height = 520
# width = 90
# line_height = 40
# one_line_length = 34
# img_complete = add_text_to_image_multiline(img_with_by, tags, font_path, font_size, font_color, height, width, line_height, one_line_length)
#
# # 6. S3にアップロードしてS3のパスを返す
# card_image_path = upload_to_s3(img_complete, card)