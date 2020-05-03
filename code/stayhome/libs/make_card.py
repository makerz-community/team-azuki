import io
import textwrap
import requests

from PIL import Image, ImageFont, ImageDraw
from allauth.socialaccount.models import SocialAccount

from ..models import Card

"""""""""""""""""""""""""""""""""""""""""""""""
TODO
- カード全体のデザイン（文字とアイコンの配置、配色とか）
  - とりあえず配置とか大きさとか折り返す文字数とかは適当
- 背景画像
- フォント
- S3へのアップロード部分

"""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""
Pillowのメモ
Image.new(): ベタ画像作成
ImageDraw.Draw(): Drawオブジェクト作成
ImageDraw.textsize(): 文字列の(length, height)を返す
ImageDraw.text(): 文字列を画像に重ねる
"""""""""""""""""""""""""""""""""""""""""""""""


# 背景画像作成
def build_base_image():
    # 背景画像の作成（とりあえずオレンジ。既存画像を使う場合は以下）
    base_image = Image.new("RGB", (1200, 630), (255, 165, 0))
    # base_image_path = "./static/画像ファイル.png"  # TODO staticのパス？
    # base_image = Image.open(base_image_path).copy()

    return base_image


# 文字入力用の関数定義（1行）
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


# 文字入力用の関数定義（複数行）
def add_text_to_image_multiline(img, text, font_path, font_size, font_color, height, width):
    # position = (width, height)
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(img)
    wrap_list = textwrap.wrap(text, 16)
    line_counter = 0
    for line in wrap_list:  # wrap_listから1行づつ取り出しlineに代入
        y = line_counter * 80 + height  # 高さ座標をline_counterに応じて下げる
        position = (width, y)
        draw.multiline_text(position, line, font_color, font=font)  # 1行分の文字列を画像に描画
        line_counter = line_counter + 1  # 行数のカウンターに1
    return img


# アイコン貼り付け用の関数定義
def add_twitter_icon(base_img, user):
# def add_twitter_icon(img):
    twitter_account_data = SocialAccount.objects.get(user_id=user.id)
    twitter_icon_url_normal = twitter_account_data.extra_data["profile_image_url_https"]
    # twitter_icon_url_normal = 'https://pbs.twimg.com/profile_images/1221399035887542272/1Mh2IfNL_normal.jpg'

    twitter_icon_url_bigger = twitter_icon_url_normal.replace("_normal", "_bigger")  # サイズが小さいのでbiggerにreplace
    icon = Image.open(io.BytesIO(requests.get(twitter_icon_url_bigger).content))  # TODO マスクかける
    img.paste(icon, (80, 134))

    return img


"""
試し
"""
base_image = build_base_image()
title = "zoomで飲み会しようようホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲホゲ"
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


"""
画像の保存（→S3にアップロードするように書き換える必要あり）
"""
file_name = "sample.png"
file_path = "./static/" + file_name

img.save(file_path)
