from django.shortcuts import render
from django.views import generic
from .models import Cards


##############
# トップページ #
##############
class TopView(generic.ListView):
    # ListViewに変更する
    template_name = "top.html"
    model = Cards


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
