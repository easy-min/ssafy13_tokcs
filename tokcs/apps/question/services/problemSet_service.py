import random
from datetime import datetime
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.contenttypes.models import ContentType

from question.models.problemSet import ProblemSet, ProblemSetQuestion
from question.models.question   import ObjectiveQuestion, SubjectiveQuestion

def create_random_problem_set(
    user, data
):
    #― 권한 검증 ―#
    if not user.is_staff:
        raise PermissionDenied("관리자만 문제 세트를 생성")

    #― 입력 데이터 ―#
    topic_id           = data['topic'].id
    chapter_ids        = [c.id for c in data['chapters']]
    total_questions    = data['total_questions']
    total_score        = data['total_score']
    objective_ratio    = data['objective_ratio']
    subjective_ratio   = data['subjective_ratio']
    scheduled_date     = data['scheduled_date']
    close_date         = data['close_date']
    title              = data.get('title') or f"랜덤 문제 세트 ({datetime.now():%Y-%m-%d %H:%M:%S})"
    description        = data.get('description', '')

    #― 문제 세트 생성 ―#
    ps = ProblemSet.objects.create(
        title           = title,
        description     = description,
        scheduled_date  = scheduled_date,
        close_date      = close_date,
        total_score     = total_score,
        pass_threshold  = data['pass_threshold']
    )

    #― 챕터 내 문제 가져오기 ―#
    from question.models.chapter import Chapter
    chapters = Chapter.objects.filter(topic__id=topic_id, id__in=chapter_ids)
    if not chapters.exists():
        raise ValidationError("선택한 챕터가 없습니다.")

    obj_qs = list(ObjectiveQuestion.objects.filter(chapter__in=chapters))
    sub_qs = list(SubjectiveQuestion.objects.filter(chapter__in=chapters))
    pool   = obj_qs + sub_qs
    if len(pool) < total_questions:
        raise ValidationError("요청한 문제 수보다 풀(객관/주관)이 적습니다.")

    selected = random.sample(pool, total_questions)

    #― ProblemSetQuestion 저장 및 배점 분배 ―#
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

    #― 배점 분배 (소수점 2자리 올림) ―#
    total_obj_score = total_score * objective_ratio / 100
    total_sub_score = total_score * subjective_ratio / 100
    obj_cnt = sum(1 for x in ps_questions if x.question.question_type=="MCQ")
    sub_cnt = sum(1 for x in ps_questions if x.question.question_type=="SA")

    per_obj = (total_obj_score / obj_cnt) if obj_cnt else 0
    per_sub = (total_sub_score / sub_cnt) if sub_cnt else 0
    per_obj = round(per_obj + 1e-6, 2)
    per_sub = round(per_sub + 1e-6, 2)

    for psq in ps_questions:
        q = psq.question
        q.score = per_obj if q.question_type=="MCQ" else per_sub
        q.save()

    return ps, ps_questions
