# question/views/objective_question_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from question.forms.objective_question_forms import ObjectiveQuestionForm
from question.services.question_creation_service import create_objective_question

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def create_objective_question_view(request):
    if request.method == 'POST':
        form = ObjectiveQuestionForm(request.POST)
        if form.is_valid():
            # 폼 데이터 추출 (객관식 문제 생성)
            question_data = {
                "chapter_id": form.cleaned_data['chapter'].id,
                "content": form.cleaned_data['content'],
                "explanation": form.cleaned_data.get('explanation', ""),
                "score": form.cleaned_data.get('score', 5),
                "question_type": "MCQ",
                # choices 텍스트를 파싱하여 선택지 리스트 생성
                "choices": [{"content": c, "is_correct": False} for c in form.cleaned_data['choices_text']]
            }
            # 예시: 첫 번째 선택지를 정답으로 지정
            if question_data["choices"]:
                question_data["choices"][0]["is_correct"] = True
            # 객관식 문제 생성 서비스 호출 (기존 service 함수 재사용)
            question = create_objective_question(request.user, question_data)
            return redirect('objective_question_detail', question_id=question.id)
    else:
        form = ObjectiveQuestionForm()
    return render(request, 'question/create_objective_question.html', {'form': form})
