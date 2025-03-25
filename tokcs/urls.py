# tokcs/urls.py
from django.urls import path
from . import views
from tokcs import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('user/mypage/', views.mypage, name='mypage'),
    path('question/create/', views.create_question, name='create_question'),
]
