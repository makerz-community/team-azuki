from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse,reverse_lazy
from django.views import generic
from .forms import CardCreateForm


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
        unfinished_form = form.save(commit=False)
        ############################################
        #request.userではないかもしれない↓↓((削除予定))
        #############################################
        unfinished_form.author = request.user
        unfinished_form.conditions = 1
        unfinished_form.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial["initial_title"] = "募集タイトルを入力してください"
        initial["initial_content"] = "例：エンジニアが集まってワイワイする予定です"
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
