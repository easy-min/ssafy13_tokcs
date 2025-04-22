# question/views/problemset_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
import datetime

# 모델 import 추가: ProblemSet 모델
from ..models.problemSet import ProblemSet

# 서비스 함수 import
from ..services.problemSet_retrieval_service import (
    get_active_problem_sets,
    get_problem_set_details,
    get_user_recent_submissions
)
from ..services.problemSet_service import create_random_problem_set  # 추가
from ..services.problemSet_service import get_user_score_for_problem_set


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


def problem_set_list_view(request):
    # 1) 전체 문제 세트 (날짜순 정렬)
    all_problem_sets = ProblemSet.objects.all().order_by('-scheduled_date')
    
    # 2) 현재 사용자 기준으로 "이미 푼 문제"와 "안 푼 문제" 구분
    user_solved_ids = set()  # 이미 푼 problem_set의 id 모음
    
    # 예시: 각 ProblemSet에 대해, user_solved, score 등 확인 (가짜 코드)
    for ps in all_problem_sets:
        score = get_user_score_for_problem_set(request.user, ps)  # 이 함수가 존재한다고 가정
        ps.score = score if score is not None else 0
        ps.pass_threshold = 70
        if score is not None:
            ps.user_solved = True
            user_solved_ids.add(ps.id)
        else:
            ps.user_solved = False

    unsolved_problem_sets = [ps for ps in all_problem_sets if not ps.user_solved]
    solved_problem_sets = [ps for ps in all_problem_sets if ps.user_solved]
    
    context = {
        'all_problem_sets': all_problem_sets,
        'unsolved_problem_sets': unsolved_problem_sets,
        'solved_problem_sets': solved_problem_sets,
    }
    return render(request, 'problemset_list.html', context)
