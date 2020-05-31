# 名前未定

リモート飲み会の募集カードを簡単に作ってTwitterでシェアできるサービスです。

## 概要

Djangoで開発中です。
環境の構築にDockerを使う形になってます。


## 機能
- トップページ(ログイン、新規作成)
- 募集作成ページ(フォーム)
- マイページ
- 一覧ページ(検索)
- 詳細ページ(応募、自分も募集するボタン)
- プレビューページ(OGP画像作成)
- シェアボタン(Twitterに投稿)


## 開発環境(requirements.txt参照)

- Python3.8.2
- asgiref==3.2.7
- boto3==1.12.39
- botocore==1.15.39
- certifi==2020.4.5.1
- chardet==3.0.4
- defusedxml==0.6.0
- Django==3.0.5
- django-allauth==0.41.0
- django-environ==0.4.5
- django-storages==1.9.1
- docutils==0.15.2
- idna==2.9
- jmespath==0.9.5
- oauthlib==3.1.0
- Pillow==7.1.1
- psycopg2==2.8.5
- python-dateutil==2.8.1
- python3-openid==3.1.0
- pytz==2019.3
- requests==2.23.0
- requests-oauthlib==1.3.0
- s3transfer==0.3.3
- six==1.14.0
- sqlparse==0.3.1
- urllib3==1.25.8

## 使用方法(AWS s3,TwitterAPIの準備が必要)
1. Dockerを[インストール](https://docs.docker.com/get-docker/)

2. 「https://github.com/makerz-community/team-azuki.git」をクローン

3. dockerを立ち上げる
    - docker-compose.ymlファイルがあるところで「docker-compose up」コマンドを実行
    - エラーになるならログを見ながら(「docker-compose logs」)、「docker-compose exec」で起動中コンテナに入って各種設定

4. http://0.0.0.0:8000 にサービスが展開されているのでアクセス


### Docker

## Dockerfileでやってること
* 作業ディレクトリの設定
* python, pipが入ってる環境でpipを最新版にアップグレード
* requirements.txtを使って依存するパッケージのインストール


## docker-composeでやってること
* アプリ用appコンテナと、postgreSQLを使うためのdbコンテナを展開
* appでport 8000をホスト側の8000にマウント
* appでホストPCのカレントディレクトリとコンテナ内のcodeディレクトリを同期
* app起動時にpython manage.py runserver 0.0.0.0:8000を実行(開発用サーバーの起動)
* dbでport 5432ををホスト側の5432にマウント
* dbのデータ保存先を設定


## ブランチ
* develop•••開発ブランチ
* master•••本番ブランチ
* mahiru,zukimaru,chihiro•••作業ブランチ
