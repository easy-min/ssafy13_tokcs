import random
from datetime import datetime
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.contenttypes.models import ContentType

from question.models.problemSet import ProblemSet, ProblemSetQuestion
from question.models.question   import ObjectiveQuestion, SubjectiveQuestion

def create_random_problem_set(user, data):
    #― 권한 검증 ―#
    if not user.is_staff:
        raise PermissionDenied("관리자만 문제 세트를 생성할 수 있습니다.")

    #― 입력 데이터 언패킹 ―#
    topic_id        = data['topic'].id
    chapter_ids     = [c.id for c in data['chapters']]
    total_questions = data['total_questions']
    total_score     = data['total_score']
    obj_ratio       = data['objective_ratio']
    sub_ratio       = data['subjective_ratio']
    scheduled_date  = data['scheduled_date']
    close_date      = data['close_date']
    title           = data.get('title') or f"랜덤 문제 세트 ({datetime.now():%Y-%m-%d %H:%M:%S})"
    description     = data.get('description', '')
    pass_threshold  = data['pass_threshold']

    #― ProblemSet 생성 ―#
    ps = ProblemSet.objects.create(
        title           = title,
        description     = description,
        scheduled_date  = scheduled_date,
        close_date      = close_date,
        total_score     = total_score,
        pass_threshold  = pass_threshold
    )

    #― 챕터 내 문제 풀 조회 ―#
    from question.models.chapter import Chapter
    chapters = Chapter.objects.filter(topic__id=topic_id, id__in=chapter_ids)
    if not chapters.exists():
        raise ValidationError("선택한 챕터가 없습니다.")

    obj_qs = list(ObjectiveQuestion.objects.filter(chapter__in=chapters))
    sub_qs = list(SubjectiveQuestion.objects.filter(chapter__in=chapters))

    #― 비율에 따른 문제 개수 계산 ―#
    obj_needed = round(total_questions * (obj_ratio / 100))
    sub_needed = total_questions - obj_needed

    if obj_needed > len(obj_qs) or sub_needed > len(sub_qs):
        raise ValidationError("풀(pool) 내에 요청한 비율만큼 문제 유형이 충분하지 않습니다.")

    #― 타입별 샘플링 ―#
    selected_obj = random.sample(obj_qs, obj_needed)
    selected_sub = random.sample(sub_qs, sub_needed)
    selected = selected_obj + selected_sub
    random.shuffle(selected)  # 순서를 섞고 싶다면

    #― ProblemSetQuestion 저장 ―#
    ps_questions = []
    for idx, q in enumerate(selected, start=1):
        ct = ContentType.objects.get_for_model(q.__class__)
        psq = ProblemSetQuestion.objects.create(
            problemset   = ps,
            content_type = ct,
            object_id    = q.id,
            order        = idx
        )
        ps_questions.append(psq)

    #― 배점 분배(소수점 둘째자리 올림) ―#
    total_obj_score = total_score * (obj_ratio / 100)
    total_sub_score = total_score * (sub_ratio / 100)
    per_obj = round(total_obj_score / obj_needed + 1e-6, 2) if obj_needed else 0
    per_sub = round(total_sub_score / sub_needed + 1e-6, 2) if sub_needed else 0

    for psq in ps_questions:
        q = psq.question
        q.score = per_obj if q.question_type == "MCQ" else per_sub
        q.save()

    return ps, ps_questions
