from datetime import date
from tokcs.question.models.problemSet import ProblemSet
from tokcs.question.services.problemSet_service import get_user_score_for_problem_set

def get_calendar_problem_sets(year: int, month: int, user):
    """
    지정한 연도와 월에 해당하는 문제 세트들을 조회하여 캘린더에 맞게 데이터를 반환합니다.
    
    각 문제 세트는 다음과 같은 딕셔너리 형태로 반환됩니다:
      - id: 문제 세트 ID
      - title: 문제 세트 제목
      - date: 문제 세트의 scheduled_date (YYYY-MM-DD 형식)
      - status: 'solved' (사용자의 점수가 요구 점수 이상일 경우) 또는 'unsolved'
      - avgScore: 사용자의 점수(없으면 0으로 처리)
      - requiredScore: 예를 들어, 총점의 80% (정수)
      
    예를 들어, total_score가 100인 문제 세트라면 requiredScore는 80으로 계산됩니다.
    """
    # 지정한 월의 시작일과 다음 월의 시작일을 계산합니다.
    start_date = date(year, month, 1)
    # month가 12월인 경우에는 다음 해의 1월 1일, 그렇지 않으면 같은 해 다음 달 1일
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    # 지정한 기간에 해당하는 문제 세트를 scheduled_date 기준으로 조회합니다.
    problem_sets = ProblemSet.objects.filter(scheduled_date__gte=start_date, scheduled_date__lt=end_date)
    
    calendar_data = []
    for ps in problem_sets:
        # get_user_score_for_problem_set: 문제 세트 전체에 대한 사용자의 점수를 계산하는 함수
        user_score = get_user_score_for_problem_set(user, ps)
        # 예로 total_score의 80%를 요구 점수로 설정
        required_threshold = ps.total_score * 0.8
        status = "solved" if user_score >= required_threshold else "unsolved"
        calendar_data.append({
            "id": ps.id,
            "title": ps.title,
            "date": ps.scheduled_date.strftime("%Y-%m-%d"),
            "status": status,
            "avgScore": user_score,
            "requiredScore": int(required_threshold),
        })
    
    return calendar_data
