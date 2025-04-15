from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tokcs.question.services.calendar_service import get_calendar_problem_sets

@login_required
def calendar_view(request):
    # 예를 들어 2025년 4월 캘린더 데이터를 가져온다고 가정합니다.
    calendar_data = get_calendar_problem_sets(2025, 4, request.user)
    # 템플릿에 calendar_data를 JSON으로 넘기거나 직접 처리할 수 있습니다.
    return render(request, 'calendar.html', {'calendar_data': calendar_data})
