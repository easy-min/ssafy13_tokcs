# question/views/subjective_question_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from question.forms.subjective_question_forms import SubjectiveQuestionForm
from question.services.question_creation_service import create_subjective_question

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def create_subjective_question_view(request):
    if request.method == 'POST':
        form = SubjectiveQuestionForm(request.POST)
        if form.is_valid():
            # 폼에서 전달된 데이터를 활용해서 주관식 문제 생성
            question_data = {
                "chapter_id": form.cleaned_data['chapter'].id,
                "content": form.cleaned_data['content'],
                "explanation": form.cleaned_data.get('explanation', ""),
                "score": form.cleaned_data.get('score', 5),
                "question_type": "SA",
                # 주관식 문제의 경우, 선택된 키워드의 ID 리스트를 전달
                "keyword_ids": [kw.id for kw in form.cleaned_data['keywords']]
            }
            question = create_subjective_question(request.user, question_data)
            return redirect('subjective_question_detail', question_id=question.id)
    else:
        form = SubjectiveQuestionForm()
    return render(request, 'question/create_subjective_question.html', {'form': form})
