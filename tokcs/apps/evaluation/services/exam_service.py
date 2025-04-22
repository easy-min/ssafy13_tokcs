from django.shortcuts          import get_object_or_404
from django.core.exceptions   import PermissionDenied
from django.utils             import timezone

from .models.exam_model       import ExamSession
from .models.answer_model     import ObjectiveAnswer, SubjectiveAnswer
from question.models.problemSet import ProblemSetQuestion

def start_exam(user, ps_id):
    """
    문제 세트(ps_id)에 대해 사용자의 ExamSession을 생성하거나 반환.
    제한 시간이 지나거나 이미 제출된 세션이 있으면 그대로 반환.
    """
    from question.models.problemSet import ProblemSet
    ps = get_object_or_404(ProblemSet, id=ps_id)
    if not ps.active:
        raise PermissionDenied("현재 풀 수 없는 문제 세트입니다.")
    session, created = ExamSession.objects.get_or_create(
        user=user,
        problemset=ps
    )
    return session

def get_exam_questions(session):
    """
    ExamSession에 묶인 문제 목록을 order 순서대로 꺼내,
    각 문항 정보를 dict로 포맷해서 리스트로 반환.
    """
    qs = ProblemSetQuestion.objects.filter(
        problemset=session.problemset
    ).order_by('order').select_related('content_type')
    questions = []
    for psq in qs:
        q = psq.question
        base = {
            'order':   psq.order,
            'type':    q.question_type,
            'content': q.content,
            'score':   q.score,
        }
        if q.question_type == 'MCQ':
            base['choices'] = [
                {'id': c.id, 'content': c.content}
                for c in q.choices.all()
            ]
        questions.append(base)
    return questions

def submit_exam(session, post_data):
    """
    POST된 답안을 저장하고, 세션을 '제출됨' 상태로 마킹.
    mcq_<order> : 객관식 답안
    sa_<order>  : 주관식 답안
    """
    if not session.is_active:
        raise PermissionDenied("제출 시간이 지났거나 이미 제출된 세션입니다.")

    # 객관식 저장
    for key, val in post_data.items():
        if key.startswith('mcq_'):
            order = int(key.split('_', 1)[1])
            choice_id = int(val)
            psq = get_object_or_404(
                ProblemSetQuestion,
                problemset=session.problemset,
                order=order
            )
            ObjectiveAnswer.objects.update_or_create(
                session=session,
                question=psq.question,
                defaults={
                    'choice_id': choice_id,
                    'submitted_at': timezone.now()
                }
            )

    # 주관식 저장
    for key, val in post_data.items():
        if key.startswith('sa_'):
            order = int(key.split('_', 1)[1])
            text = val.strip()
            psq = get_object_or_404(
                ProblemSetQuestion,
                problemset=session.problemset,
                order=order
            )
            SubjectiveAnswer.objects.update_or_create(
                session=session,
                question=psq.question,
                defaults={
                    'answer_text': text,
                    'submitted_at': timezone.now()
                }
            )

    # 세션 제출 처리
    session.is_submitted = True
    session.end_time     = timezone.now()
    session.save()
    return session

def grade_exam(session):
    """
    세션에 기록된 답안을 바탕으로 최종 점수 계산(객관식 정답 가중치 + 주관식 score).
    """
    total = 0
    # 객관식 채점
    for ans in ObjectiveAnswer.objects.filter(session=session).select_related('question__choice'):
        if ans.choice.is_correct:
            total += ans.question.score
    # 주관식 점수 합산
    for ans in SubjectiveAnswer.objects.filter(session=session):
        total += ans.score
    return total
