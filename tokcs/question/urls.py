from django.urls import path
from .views import (
    objective_question_views,
    problemSet_views,
    subjective_question_views,
)
from tokcs.question.views.solve_views import solve_problems_view
from .views.create_problem_view import create_problem_view  # 새로 만든 뷰 import
from .views.objective_question_views import create_objective_question_view, objective_question_detail_view  # 새로운 상세 뷰 추가
from .views.subjective_question_views import subjective_question_detail_view

urlpatterns = [
    # 문제 세트 관련 URL
    path('problemset/create/', problemSet_views.create_random_problem_set_view, name='create_random_problem_set'),
    path('problemset/<int:ps_id>/', problemSet_views.problem_set_detail_view, name='problem_set_detail'),
    path('problemset/active/', problemSet_views.active_problem_set_list_view, name='active_problem_set_list'),
    path('problemset/submissions/', problemSet_views.user_recent_submissions_view, name='user_recent_submissions'),
    path('problemset/list/', problemSet_views.problem_set_list_view, name='problem_set_list'),
 
    path('objective/create/', objective_question_views.create_objective_question_view, name='create_objective_question'),
    # 추가된 objective_question_detail_view URL 패턴 (변경 없음)
    path('objective/<int:question_id>/', objective_question_detail_view, name='objective_question_detail'),
    path('subjective/create/', subjective_question_views.create_subjective_question_view, name='create_subjective_question'),
    path('subjective/<int:question_id>/', subjective_question_detail_view, name='subjective_question_detail'),
    # 다른 URL 패턴...
    # 문제 풀기 URL
    path('solve/', solve_problems_view, name='solve_problems'),
    
    # 문제 내러가기 화면 (객관식, 주관식 선택)
    path('create/', create_problem_view, name='create_problem'),
]
