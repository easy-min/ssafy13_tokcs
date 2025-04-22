# question/views/create_problem_view.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def create_problem_view(request):
    # 이 뷰는 객관식과 주관식 문제 생성 페이지로 이동할 수 있는 버튼이 있는 템플릿을 렌더링합니다.
    return render(request, 'question/user/create_problem.html')

