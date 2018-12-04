# from django.conf.urls import url
from django.urls import path
from main import views

urlpatterns = [

    path('', views.index, name='main_index_index'),
]
