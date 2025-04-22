# question/services/problemset_retrieval_service.py

from django.shortcuts import get_object_or_404
from question.models.problemSet import ProblemSetQuestion

def get_problem_set_preview(ps_id):
    """
    문제 세트(ps_id)에 포함된 모든 문제를 '미리 보기'용으로 구성해서 반환합니다.
    각 문제에 대해:
      - question_type: 'MCQ' or 'SA'
      - content: 문제 내용
      - choices: [(선택지 문자열, is_correct), ...] (객관식만)
      - keywords: [키워드 리스트] (주관식만)
      - explanation: 해설
      - score: 배점
      - order: 순서
    """
    # get_object_or_404를 쓰면 PS가 없을 땐 404
    psq_qs = ProblemSetQuestion.objects.filter(
        problemset__id=ps_id
    ).select_related('content_type').order_by('order')
    if not psq_qs:
        raise Http404("해당 문제 세트를 찾을 수 없습니다.")

    preview = {
        'problemset': psq_qs.first().problemset,  # ProblemSet 인스턴스
        'questions': []
    }
    for psq in psq_qs:
        q = psq.question
        item = {
            'order':     psq.order,
            'type':      q.question_type,
            'content':   q.content,
            'explanation': q.explanation,
            'score':     q.score,
        }
        if q.question_type == 'MCQ':
            # choices.related_name='choices'
            item['choices'] = [
                {'content': c.content, 'is_correct': c.is_correct}
                for c in q.choices.all()
            ]
        else:  # 'SA'
            item['keywords'] = [kw.word for kw in q.keywords.all()]
        preview['questions'].append(item)

    return preview
