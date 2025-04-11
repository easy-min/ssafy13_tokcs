# question/views/objective_question_views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from question.services.question_creation_service import create_objective_question

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def create_objective_question_view(request):
    if request.method == 'POST':
        # 기본 필드들 추출
        chapter_id = request.POST.get('chapter')
        content = request.POST.get('content', '').strip()
        explanation = request.POST.get('explanation', '').strip()
        try:
            score = int(request.POST.get('score', 5))
        except ValueError:
            score = 5
        
        # 동적으로 추가된 선택지 데이터 추출 (빈 값은 제외)
        choices_list = request.POST.getlist('choices[]')
        choices_clean = [c.strip() for c in choices_list if c.strip()]
        if len(choices_clean) < 2:
            error = "최소 2개의 선택지를 입력해야 합니다."
            # 단원 목록을 다시 전달하도록 chapter 리스트를 불러옴.
            from question.models.chapter import Chapter
            chapters = Chapter.objects.all()
            return render(request, 'question/create_objective_question.html', {
                'error': error,
                'chapters': chapters
            })
        
        # 정답 지정 (라디오 버튼에서 선택된 값을 인덱스로 처리)
        correct_choice_index = request.POST.get('correct_choice')
        try:
            correct_choice_index = int(correct_choice_index)
        except (TypeError, ValueError):
            correct_choice_index = 0
        
        # 선택지 리스트 구성: 인덱스가 correct_choice_index인 항목은 정답으로 지정
        choices = []
        for i, choice_text in enumerate(choices_clean):
            choices.append({
                'content': choice_text,
                'is_correct': (i == correct_choice_index)
            })
        
        question_data = {
            'chapter_id': int(chapter_id),
            'content': content,
            'explanation': explanation,
            'score': score,
            'question_type': 'MCQ',
            'choices': choices,
        }
        question = create_objective_question(request.user, question_data)
        return redirect('objective_question_detail', question_id=question.id)
    else:
        # GET 요청: 단원 목록을 컨텍스트로 전달 (템플릿의 select 요소 사용)
        from question.models.chapter import Chapter
        chapters = Chapter.objects.all()
        return render(request, 'question/create_objective_question.html', {'chapters': chapters})
