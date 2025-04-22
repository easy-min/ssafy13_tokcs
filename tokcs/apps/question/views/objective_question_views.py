from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..services.question_creation_service import create_objective_question
from ..models.chapter import Chapter
from ..models.topic import Topic
from ..models.question import ObjectiveQuestion

@login_required
def create_objective_question_view(request):
    if request.method == 'POST':
        # 필드 추출
        chapter_id = request.POST.get('chapter')
        content = request.POST.get('content', '').strip()
        explanation = request.POST.get('explanation', '').strip()
        try:
            score = int(request.POST.get('score', 5))
        except ValueError:
            score = 5

        # 선택지 처리
        choices_list = request.POST.getlist('choices[]')
        choices_clean = [c.strip() for c in choices_list if c.strip()]
        if len(choices_clean) < 2:
            error = "최소 2개의 선택지를 입력해야 합니다."
            topics = Topic.objects.all()
            chapters = Chapter.objects.all()
            return render(request, 'question/user/create_objective_question.html', {
                'error': error,
                'topics': topics,
                'chapters': chapters
            })

        # 정답 지정 (1부터 시작)
        correct_choice_index = request.POST.get('correct_choice')
        try:
            correct_choice_index = int(correct_choice_index)
        except (TypeError, ValueError):
            correct_choice_index = 0

        choices = []
        for i, choice_text in enumerate(choices_clean):
            choices.append({
                'content': choice_text,
                'is_correct': ((i + 1) == correct_choice_index)
            })

        question_data = {
            'chapter_id': int(chapter_id),
            'content': content,
            'explanation': explanation,
            'score': score,
            'question_type': 'MCQ',
            'choices': choices,
        }

        # 문제 생성
        question = create_objective_question(request.user, question_data)

        # 어떤 버튼으로 제출했는지 확인
        submit_type = request.POST.get('submit_type')
        if submit_type == 'continue':
            return redirect('create_objective_question')  # 같은 페이지로 리디렉션
        return redirect('objective_question_detail', question_id=question.id)

    else:
        topics = Topic.objects.all()
        chapters = Chapter.objects.all()
        return render(request, 'question/user/create_objective_question.html', {
            'topics': topics,
            'chapters': chapters
        })

@login_required
def objective_question_detail_view(request, question_id):
    question = get_object_or_404(ObjectiveQuestion, id=question_id)
    return render(request, 'question/user/objective_question_detail.html', {
        'question': question
    })
