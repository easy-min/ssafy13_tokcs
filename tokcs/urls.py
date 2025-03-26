# tokcs/urls.py
from django.urls import path
from . import views
from tokcs import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('user/mypage/', views.mypage, name='mypage'),
    path('user/profile/', views.profile, name='profile'), #내 정보 보기
    path('quiz/user/create_subjective_quiz/', views.create_subjective_quiz, name='create_subjective_quiz'),
    path('quiz/start/', views.quiz_start, name='quiz_start'),  # ✅ 문제 풀러가기
    #path('quiz/review/<int:history_id>/', views.review_wrong, name='review_wrong'),
    path('quiz/admin/create_daily_quiz/', views.create_daily_quiz, name='create_daily_quiz'),
    path('quiz/admin/daily_quiz_list/', views.daily_quiz_list, name = 'daily_quiz_list'),
    path('quiz/result/<int:day_quiz_id>/', views.quiz_result, name='quiz_result'),
    path('quiz/admin/grade/<int:day_quiz_id>/', views.grade_user_answers, name='grade_user_answers'),
    path('user/profile/', views.profile, name='profile'),  # 내 정보 보기
]
