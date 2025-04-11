# question/views/problemset_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
import datetime

# 올바른 import 구문: 각 함수들이 정의된 파일에서 가져옵니다.
from question.services.problemSet_retrieval_service import (
    get_active_problem_sets,
    get_problem_set_details,
    get_user_recent_submissions
)
from question.services.problemSet_service import create_random_problem_set  # 추가

# 관리자 권한 체크 함수
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def create_random_problem_set_view(request):
    if request.method == 'POST':
        try:
            topic_id = int(request.POST.get('topic_id'))
            # chapter_ids는 예: "1,3,5" 형식의 문자열
            chapter_ids_str = request.POST.get('chapter_ids', '')
            chapter_ids = [int(ch.strip()) for ch in chapter_ids_str.split(',') if ch.strip()]
            total_questions = int(request.POST.get('total_questions'))
            total_score = int(request.POST.get('total_score'))
            objective_ratio = int(request.POST.get('objective_ratio'))
            subjective_ratio = int(request.POST.get('subjective_ratio'))
            scheduled_date = datetime.datetime.strptime(request.POST.get('scheduled_date'), '%Y-%m-%d').date()
            close_date = datetime.datetime.strptime(request.POST.get('close_date'), '%Y-%m-%d').date()
        except Exception as e:
            return render(request, 'problemset/create_random_problem_set.html', {'error': f"입력 값 오류: {str(e)}"})
        
        try:
            problem_set, ps_questions = create_random_problem_set(
                request.user,
                topic_id,
                chapter_ids,
                total_questions,
                total_score,
                objective_ratio,
                subjective_ratio,
                scheduled_date,
                close_date
            )
            return redirect('problem_set_detail', ps_id=problem_set.id)
        except Exception as e:
            return render(request, 'problemset/create_random_problem_set.html', {'error': str(e)})
    
    return render(request, 'problemset/create_random_problem_set.html')

@login_required
def active_problem_set_list_view(request):
    from datetime import date
    problem_sets = get_active_problem_sets()  # 활성화된 문제 세트 조회 서비스 함수
    context = {'problem_sets': problem_sets, 'today': date.today()}
    return render(request, 'problemset/active_problem_sets.html', context)

@login_required
def problem_set_detail_view(request, ps_id):
    details = get_problem_set_details(ps_id)
    if not details:
        return render(request, 'problemset/problem_set_detail.html', {'error': "문제 세트를 찾을 수 없습니다."})
    context = {'problem_set': details}
    return render(request, 'problemset/problem_set_detail.html', context)

@login_required
def user_recent_submissions_view(request):
    submissions = get_user_recent_submissions(request.user, limit=5)
    return render(request, 'problemset/user_recent_submissions.html', {'submissions': submissions})
