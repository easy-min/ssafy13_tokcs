# question/views/objective_question_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from tokcs.apps.question.forms.objective_question_forms import ObjectiveQuestionForm, ChoiceFormSet
from tokcs.apps.question.models.chapter import Chapter
from tokcs.apps.question.models.topic import Topic


def is_admin(user):
    return user.is_staff

@login_required
def create_objective_question_view(request):
    topics   = Topic.objects.all()
    chapters = Chapter.objects.all()

    if request.method == 'POST':
        form    = ObjectiveQuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # 삭제되지 않은 유효한 선택지 개수 계산
            valid_choices = [
                cd for cd in formset.cleaned_data
                if cd and not cd.get('DELETE', False)
            ]
            choice_count = len(valid_choices)

            # 2개 이상, 7개 이하 검증
            if choice_count < 2 or choice_count > 7:
                error = "선택지는 2개 이상, 7개 이하로 입력해야 합니다."
                return render(request, 'question/user/create_objective_question.html', {
                    'form':    form,
                    'formset': formset,
                    'topics':  topics,
                    'chapters': chapters,
                    'error':   error,
                })

            # 1) Question 저장 준비
            question = form.save(commit=False)
            question.creator       = request.user
            question.question_type = 'MCQ'
            question.save()

            # 2) Choice formset 저장
            formset.instance = question
            formset.save()

            # 3) 계속/완료 분기
            if request.POST.get('submit_type') == 'continue':
                return redirect('create_objective_question')
            return redirect('objective_question_detail', question_id=question.id)

    else:
        form    = ObjectiveQuestionForm()
        formset = ChoiceFormSet()

    return render(request, 'question/user/create_objective_question.html', {
        'form':     form,
        'formset':  formset,
        'topics':   topics,
        'chapters': chapters,
    })
