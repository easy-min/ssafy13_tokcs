# problemSet_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseForbidden
import datetime

# 서비스 함수 임포트
from problemset_service import (
    create_random_problem_set,
    create_problem_set,
    add_multiple_questions_to_problem_set
)
from problemset_retrieval_service import (
    get_active_problem_sets,
    get_problem_set_details,
    get_user_recent_submissions
)

# ----------------------------------------------------------------
# 관리자 체크 함수
def is_admin(user):
    return user.is_staff

# ----------------------------------------------------------------
# [일반 사용자] 활성화된 문제 세트 목록 조회
@login_required
def active_problem_set_list(request):
    problem_sets = get_active_problem_sets()
    context = {
        'problem_sets': problem_sets
    }
    return render(request, 'problemset/active_problem_sets.html', context)

# ----------------------------------------------------------------
# [일반 사용자] 특정 문제 세트 세부 정보 조회
@login_required
def problem_set_detail(request, ps_id):
    details = get_problem_set_details(ps_id)
    if not details:
        return HttpResponse("문제 세트를 찾을 수 없습니다.", status=404)
    context = {
        'problem_set': details,
    }
    return render(request, 'problemset/problem_set_detail.html', context)

# ----------------------------------------------------------------
# [관리자] 랜덤 문제 세트 생성 뷰
@login_required
@user_passes_test(is_admin)
def create_random_problem_set_view(request):
    if request.method == 'POST':
        try:
            topic_id = int(request.POST.get('topic_id'))
            # chapter_ids를 콤마로 구분된 문자열로 전송한다고 가정
            chapter_ids_str = request.POST.get('chapter_ids', "")
            chapter_ids = [int(ch) for ch in chapter_ids_str.split(',') if ch.strip()]
            total_questions = int(request.POST.get('total_questions'))
            total_score = int(request.POST.get('total_score'))
            objective_ratio = int(request.POST.get('objective_ratio'))
            subjective_ratio = int(request.POST.get('subjective_ratio'))
            # 날짜 문자열('YYYY-MM-DD')을 date 객체로 변환
            scheduled_date = datetime.datetime.strptime(request.POST.get('scheduled_date'), '%Y-%m-%d').date()
            close_date = datetime.datetime.strptime(request.POST.get('close_date'), '%Y-%m-%d').date()
        except Exception as e:
            return render(request, 'problemset/create_random_problem_set.html', {'error': f"입력 값 오류: {str(e)}"})
        
        try:
            problem_set, psq_list = create_random_problem_set(
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

    # GET 요청: 문제 세트 생성 폼을 보여줌
    return render(request, 'problemset/create_random_problem_set.html')

# ----------------------------------------------------------------
# [일반 사용자] 사용자의 최근 제출 내역 조회 뷰
@login_required
def user_recent_submissions_view(request):
    submissions = get_user_recent_submissions(request.user, limit=5)
    context = {
        'submissions': submissions
    }
    return render(request, 'problemset/user_recent_submissions.html', context)
