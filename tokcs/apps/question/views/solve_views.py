# tokcs/question/solve_views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def solve_problems_view(request):
    # 여기에 문제 풀기 페이지의 실제 로직을 구현하세요.
    return render(request, 'question/solve_problems.html')
