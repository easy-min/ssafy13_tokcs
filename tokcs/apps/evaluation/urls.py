from django.urls import path
from . import views

urlpatterns = [
    path('start/<int:ps_id>/',    views.exam_start_view,  name='exam_start'),
    path('take/<int:session_id>/', views.exam_take_view,   name='exam_take'),
    path('result/<int:session_id>/', views.exam_result_view, name='exam_result'),
]
