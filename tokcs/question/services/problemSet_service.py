import random
from datetime import datetime
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.contenttypes.models import ContentType

from tokcs.question.models.problemSet import ProblemSet, ProblemSetQuestion
from tokcs.question.models.chapter import Chapter
from tokcs.question.models.question import ObjectiveQuestion, SubjectiveQuestion
from tokcs.question.services.question_creation_service import (
    create_objective_question,
    create_subjective_question
)

# 배점 분배 유틸리티; 아래 함수가 정의되어 있다고 가정합니다.
def distribute_scores_for_problem_set(problem_set, ps_questions, objective_ratio, subjective_ratio):
    objective_questions = [psq for psq in ps_questions if psq.question.question_type == "MCQ"]
    subjective_questions = [psq for psq in ps_questions if psq.question.question_type == "SA"]

    objective_count = len(objective_questions)
    subjective_count = len(subjective_questions)

    total = problem_set.total_score
    total_objective_score = total * (objective_ratio / 100)
    total_subjective_score = total * (subjective_ratio / 100)

    per_obj_score = total_objective_score / objective_count if objective_count else 0
    per_subj_score = total_subjective_score / subjective_count if subjective_count else 0

    for psq in objective_questions:
        question = psq.question
        question.score = per_obj_score
        question.save()
    for psq in subjective_questions:
        question = psq.question
        question.score = per_subj_score
        question.save()
    return per_obj_score, per_subj_score

def create_problem_set(user, data):
    if not user.is_staff:
        raise PermissionDenied("문제 세트 출제 권한이 없습니다.")
    
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

def add_question_to_problem_set(user, problem_set, question_type, question_data, order):
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

def add_multiple_questions_to_problem_set(user, problem_set, questions_list):
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

def create_random_problem_set(user,
                              topic_id,
                              chapter_ids,
                              total_questions,
                              total_score,
                              objective_ratio,
                              subjective_ratio,
                              scheduled_date,
                              close_date):
    if not user.is_staff:
        raise PermissionDenied("문제 세트 출제 권한이 없습니다.")
        
    if objective_ratio + subjective_ratio != 100:
        raise ValidationError("객관식과 주관식 배점 비율의 합은 100이어야 합니다.")
    
    ps_data = {
        "title": f"랜덤 문제 세트 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
        "description": "자동 생성된 랜덤 문제 세트",
        "scheduled_date": scheduled_date,
        "close_date": close_date,
        "total_score": total_score,
    }
    problem_set = create_problem_set(user, ps_data)
    
    from tokcs.question.models.chapter import Chapter
    chapters = Chapter.objects.filter(topic__id=topic_id, id__in=chapter_ids)
    if not chapters.exists():
        raise ValidationError("선택한 챕터가 존재하지 않습니다.")
    
    objective_questions = list(ObjectiveQuestion.objects.filter(chapter__in=chapters))
    subjective_questions = list(SubjectiveQuestion.objects.filter(chapter__in=chapters))
    all_questions = objective_questions + subjective_questions
    if len(all_questions) < total_questions:
        raise ValidationError("선택한 챕터 내의 문제 수가 요청한 총 문제 수보다 적습니다.")
    
    selected_questions = random.sample(all_questions, total_questions)
    
    psq_list = []
    for order, question in enumerate(selected_questions, start=1):
        content_type = ContentType.objects.get_for_model(question.__class__)
        from tokcs.question.models.problemSet import ProblemSetQuestion
        psq = ProblemSetQuestion.objects.create(
            problemset=problem_set,
            content_type=content_type,
            object_id=question.id,
            order=order
        )
        psq_list.append(psq)
    
    distribute_scores_for_problem_set(problem_set, psq_list, objective_ratio, subjective_ratio)
    
    return problem_set, psq_list

def get_user_score_for_problem_set(user, problem_set):
    return grade_problem_set(problem_set, user)

def grade_problem_set(problem_set, user):
    """
    특정 문제 세트에 포함된 모든 문제(ProblemSetQuestion)를 순회하며,
    해당 문제의 채점 결과(각 문제의 score)를 합산하여 전체 점수를 계산합니다.
    """
    total_score = 0
    # 문제 세트에 포함된 문제들을 order 기준으로 정렬하여 조회
    ps_questions = problem_set.problems.all().order_by('order')
    
    for psq in ps_questions:
        question = psq.question
        if question.question_type == 'MCQ':
            try:
                # 사용자의 객관식 답안을 조회합니다.
                answer = question.objectiveanswer_set.filter(user=user).first()
                if answer:
                    total_score += answer.score
            except Exception:
                pass  # 응답 없으면 0점 처리
        elif question.question_type == 'SA':
            try:
                # 사용자의 주관식 답안을 조회합니다.
                answer = question.subjectiveanswer_set.filter(user=user).first()
                if answer:
                    total_score += answer.score
            except Exception:
                pass
    return total_score

def get_user_score_for_problem_set(user, problem_set):
    """
    지정된 문제 세트와 사용자에 대해 전체 점수를 반환합니다.
    """
    return grade_problem_set(problem_set, user)
