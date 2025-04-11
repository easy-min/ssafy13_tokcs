# problemSet_retrieval_service.py

from datetime import date
from django.db.models import Prefetch
from question.models.problemSet import ProblemSet, ProblemSetQuestion
from question.models.choice import ObjectiveAnswer, SubjectiveAnswer
from django.contrib.auth import get_user_model

User = get_user_model()

def get_active_problem_sets():
    """
    활성화된 문제 세트 조회 서비스.
    
    조건:
      - scheduled_date <= 오늘 < close_date
      - is_active 필드가 True인 경우 (자동 활성화 스케줄러나 check_and_update_activation() 메서드에 의해 업데이트됨)
      
    반환:
      - 활성화된 ProblemSet QuerySet
    """
    today = date.today()
    # is_active 필드도 True인 문제 세트를 필터링합니다.
    return ProblemSet.objects.filter(scheduled_date__lte=today, close_date__gt=today, is_active=True)


def get_problem_set_details(problem_set_id):
    """
    특정 문제 세트의 세부 정보를 조회하는 서비스.
    
    동작:
      - 문제 세트의 기본 정보와 함께, 문제 세트에 포함된 문제(ProblemSetQuestion)들을 order 기준으로 정렬하여 조회합니다.
      
    반환:
      - 문제 세트 상세 정보를 담은 dict
      - 존재하지 않으면 None 반환
    """
    try:
        problem_set = ProblemSet.objects.get(id=problem_set_id)
    except ProblemSet.DoesNotExist:
        return None
    
    # 문제 세트 내 문제들을 order 순으로 미리 로딩합니다.
    ps_questions = problem_set.problems.all().order_by('order')
    details = {
        'title': problem_set.title,
        'description': problem_set.description,
        'scheduled_date': problem_set.scheduled_date,
        'close_date': problem_set.close_date,
        'total_score': problem_set.total_score,
        'is_active': problem_set.is_active,
        'created_at': problem_set.created_at,
        'questions': list(ps_questions)  # 필요 시 serialize해서 넘길 수 있음.
    }
    return details


def get_user_recent_submissions(user, limit=5):
    """
    사용자의 최근 제출 내역을 조회하는 서비스.
    
    동작:
      - ObjectiveAnswer와 SubjectiveAnswer를 합쳐서 최근 제출 시간(created_at)을 기준으로 정렬 후,
        상위 limit 건을 반환합니다.
        
    반환:
      - 최근 제출 Answer 객체들의 리스트 (객관식, 주관식 모두 포함)
    """
    from django.db.models import Q
    # 각각의 답안 객체들을 최근 생성일 역순으로 가져옵니다.
    objective_qs = ObjectiveAnswer.objects.filter(user=user).select_related('question').order_by('-created_at')[:limit]
    subjective_qs = SubjectiveAnswer.objects.filter(user=user).select_related('question').order_by('-created_at')[:limit]
    
    # 두 queryset을 리스트로 변환하여 병합합니다.
    submissions = list(objective_qs) + list(subjective_qs)
    # 생성일(created_at)을 기준으로 내림차순 정렬합니다.
    submissions.sort(key=lambda x: x.created_at, reverse=True)
    
    # 최종 결과로 상위 limit 건만 반환합니다.
    return submissions[:limit]
