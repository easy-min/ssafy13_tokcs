# problemSet_service.py

import random
from datetime import date, datetime
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.contenttypes.models import ContentType

# 모델 임포트
from question.models.problemSet import ProblemSet, ProblemSetQuestion
from question.models.chapter import Chapter
from question.models.question import ObjectiveQuestion, SubjectiveQuestion
# 기존 문제 생성 서비스 재사용 (각 문제별 상세 생성 로직)
from question.services.question_creation_service import (
    create_objective_question,
    create_subjective_question
)
# 배점 분배 유틸리티 (score_distribution_service 파일에 정의된 distribute_scores_for_problem_set)
# 만약 score_distribution_service가 없으면 아래 함수 내용을 그대로 사용하면 됩니다.
def distribute_scores_for_problem_set(problem_set, ps_questions, objective_ratio, subjective_ratio):
    """
    문제 세트에 포함된 문제들에 대해, 
    객관식/주관식 비율(objective_ratio, subjective_ratio)을 반영하여 각 문제의 배점을 설정합니다.

    - 문제 세트의 총점(total_score) 기준:
         객관식 문제 총점 = total_score * (objective_ratio/100)
         주관식 문제 총점 = total_score * (subjective_ratio/100)
    - 각 문제의 배점은 유형별 문제 수에 따라 분배됩니다.
    """
    # 객관식과 주관식 문제 분리
    objective_questions = [psq for psq in ps_questions if psq.question.question_type == "MCQ"]
    subjective_questions = [psq for psq in ps_questions if psq.question.question_type == "SA"]

    objective_count = len(objective_questions)
    subjective_count = len(subjective_questions)

    total = problem_set.total_score
    total_objective_score = total * (objective_ratio / 100)
    total_subjective_score = total * (subjective_ratio / 100)

    per_obj_score = total_objective_score / objective_count if objective_count else 0
    per_subj_score = total_subjective_score / subjective_count if subjective_count else 0

    # 문제마다 score 필드 업데이트
    for psq in objective_questions:
        question = psq.question
        question.score = per_obj_score
        question.save()
    for psq in subjective_questions:
        question = psq.question
        question.score = per_subj_score
        question.save()
    return per_obj_score, per_subj_score

# ----------------------------------------------------------
# 1. 문제 세트 생성 서비스

def create_problem_set(user, data):
    """
    문제 세트를 생성하는 함수.
    
    data 예시:
    {
      "title": "2023년 말 시험",
      "description": "최종 평가 문제 세트",
      "scheduled_date": "2023-12-20",  # date 객체 혹은 'YYYY-MM-DD' 문자열
      "close_date": "2023-12-25",
      "total_score": 100
    }
    """
    if not user.is_staff:
        raise PermissionDenied("문제 세트 출제 권한이 없습니다.")
    
    # scheduled_date와 close_date가 문자열이면 date 객체로 변환 (여기서는 간단하게 처리)
    # 실제 서비스에서는 추가 검증 로직 필요
    # 예: datetime.strptime(data['scheduled_date'], "%Y-%m-%d").date()
    scheduled_date = data['scheduled_date']
    close_date = data['close_date']
    
    problem_set = ProblemSet.objects.create(
        title=data.get('title', "문제 세트"),
        description=data.get('description', ""),
        scheduled_date=scheduled_date,
        close_date=close_date,
        total_score=data.get('total_score', 100)
    )
    return problem_set

# ----------------------------------------------------------
# 2. 문제 세트에 단일 문제 추가 서비스
def add_question_to_problem_set(user, problem_set, question_type, question_data, order):
    """
    문제 세트에 개별 문제를 추가하는 함수.
    
    파라미터:
      - user: 문제 출제 권한을 가진 사용자 (권한 체크)
      - problem_set: ProblemSet 인스턴스
      - question_type: "MCQ" 또는 "SA"
      - question_data: 각 문제 생성에 필요한 데이터 (객관식은 선택지 포함, 주관식은 키워드 ID 리스트 등)
      - order: 문제 세트 내 순서
    """
    if not user.is_staff:
        raise PermissionDenied("문제 출제 권한이 없습니다.")

    if question_type == "MCQ":
        question = create_objective_question(user, question_data)
    elif question_type == "SA":
        question = create_subjective_question(user, question_data)
    else:
        raise ValidationError("유효하지 않은 문제 유형입니다.")
    
    content_type = ContentType.objects.get_for_model(question.__class__)
    ps_question = ProblemSetQuestion.objects.create(
        problemset=problem_set,
        content_type=content_type,
        object_id=question.id,
        order=order
    )
    return ps_question

# ----------------------------------------------------------
# 3. 문제 세트에 여러 문제를 한 번에 추가하는 서비스
def add_multiple_questions_to_problem_set(user, problem_set, questions_list):
    """
    문제 세트에 여러 문제를 추가하는 함수.
    
    questions_list는 각 항목이 다음 형식의 dict입니다:
    {
         "question_type": "MCQ" 또는 "SA",
         "question_data": { ... },  # 각 문제 생성에 필요한 데이터
         "order": 정수 (문제 세트 내 순서)
    }
    """
    results = []
    errors = []
    for idx, q in enumerate(questions_list):
        q_type = q.get("question_type")
        q_data = q.get("question_data")
        order = q.get("order", idx + 1)
        try:
            ps_question = add_question_to_problem_set(user, problem_set, q_type, q_data, order)
            results.append(ps_question)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})
    
    if errors:
        raise ValidationError(errors)
    return results

# ----------------------------------------------------------
# 4. 전체 문제 세트 생성 및 랜덤 문제 선택 서비스
def create_random_problem_set(user,
                              topic_id,
                              chapter_ids,
                              total_questions,
                              total_score,
                              objective_ratio,
                              subjective_ratio,
                              scheduled_date,
                              close_date):
    """
    주어진 Topic 내 선택된 Chapter들에서 문제를 랜덤으로 추출하여 문제 세트를 생성합니다.
    
    파라미터:
      - user: 문제 세트 출제 권한을 가진 사용자
      - topic_id: 선택된 Topic의 ID
      - chapter_ids: 선택된 Chapter들의 ID 리스트
      - total_questions: 문제 세트에 포함할 총 문제 수
      - total_score: 문제 세트의 총점
      - objective_ratio: 객관식 문제의 배점 비율 (예: 70)
      - subjective_ratio: 주관식 문제의 배점 비율 (예: 30)
            → 두 비율의 합은 100이어야 합니다.
      - scheduled_date: 문제 세트 활성화 시작 날짜
      - close_date: 문제 세트 마감 날짜
    
    동작:
      1. 문제 세트를 생성합니다.
      2. 선택된 Topic의 해당 Chapter들을 가져옵니다.
      3. 선택된 Chapter들 내의 모든 객관식 및 주관식 문제들을 모아
         total_questions 개를 랜덤 추출합니다.
      4. 선택된 문제들을 ProblemSetQuestion에 추가하며 순서를 지정합니다.
      5. 배점 분배 함수를 호출하여, 객관식/주관식 비율에 따라 각 문제의 score를 업데이트합니다.
    
    반환:
      (problem_set, list_of_problem_set_questions)
    """
    if not user.is_staff:
        raise PermissionDenied("문제 세트 출제 권한이 없습니다.")
        
    if objective_ratio + subjective_ratio != 100:
        raise ValidationError("객관식과 주관식 배점 비율의 합은 100이어야 합니다.")
    
    # 1. 문제 세트 생성
    ps_data = {
        "title": f"랜덤 문제 세트 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
        "description": "자동 생성된 랜덤 문제 세트",
        "scheduled_date": scheduled_date,
        "close_date": close_date,
        "total_score": total_score,
    }
    problem_set = create_problem_set(user, ps_data)
    
    # 2. 선택된 Topic 및 Chapter들 가져오기
    from question.models.chapter import Chapter  # 필요시 재임포트
    chapters = Chapter.objects.filter(topic__id=topic_id, id__in=chapter_ids)
    if not chapters.exists():
        raise ValidationError("선택한 챕터가 존재하지 않습니다.")
    
    # 3. 선택된 Chapter들 내의 모든 문제(객관식, 주관식) 모으기
    objective_questions = list(ObjectiveQuestion.objects.filter(chapter__in=chapters))
    subjective_questions = list(SubjectiveQuestion.objects.filter(chapter__in=chapters))
    all_questions = objective_questions + subjective_questions
    if len(all_questions) < total_questions:
        raise ValidationError("선택한 챕터 내의 문제 수가 요청한 총 문제 수보다 적습니다.")
    
    selected_questions = random.sample(all_questions, total_questions)
    
    # 4. ProblemSetQuestion에 문제 연결 (순서 지정)
    psq_list = []
    for order, question in enumerate(selected_questions, start=1):
        content_type = ContentType.objects.get_for_model(question.__class__)
        psq = ProblemSetQuestion.objects.create(
            problemset=problem_set,
            content_type=content_type,
            object_id=question.id,
            order=order
        )
        psq_list.append(psq)
    
    # 5. 배점 분배: 객관식/주관식 문제 비율에 따라 각 문제의 score 업데이트
    distribute_scores_for_problem_set(problem_set, psq_list, objective_ratio, subjective_ratio)
    
    return problem_set, psq_list
