from django.urls import path
from . import views
from.views import TopView, CardCreateView, CardPreviewView, TwitterShareView, OtameshiView

app_name = 'stayhome'
urlpatterns = [
    path('', TopView.as_view(), name="top"),
    path('input/', CardCreateView.as_view(), name="input"),
    path('output/', CardPreviewView.as_view(), name="preview"),
    path('share/', TwitterShareView.as_view(), name="share"),
    path('otameshi/', OtameshiView.as_view(), name="otameshi")
]