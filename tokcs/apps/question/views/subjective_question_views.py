# question/views/subjective_question_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms.subjective_question_forms import SubjectiveQuestionForm, QuestionKeywordFormSet
from ..models.question import SubjectiveQuestion

@login_required
def create_subjective_question_view(request):
    topics   = Topic.objects.all()
    chapters = Chapter.objects.all()

    if request.method == 'POST':
        form    = SubjectiveQuestionForm(request.POST)
        formset = QuestionKeywordFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # 1) SubjectiveQuestion 저장 준비
            question = form.save(commit=False)
            question.creator       = request.user
            question.question_type = 'SA'            # 문제 유형 명시
            question.save()

            # 2) through 모델(QuestionKeywordMapping) 저장
            formset.instance = question
            formset.save()

            # 3) 계속 출제 / 완료 선택 처리
            submit_type = request.POST.get('submit_type', 'finish')
            if submit_type == 'continue':
                return redirect('create_subjective_question')
            return redirect('subjective_question_detail', question_id=question.id)

    else:
        form    = SubjectiveQuestionForm()
        formset = QuestionKeywordFormSet()

    return render(request, 'question/user/create_subjective_question.html', {
        'form':    form,
        'formset': formset,
        'topics':  topics,
        'chapters': chapters,
    })


@login_required
def subjective_question_detail_view(request, question_id):
    question = get_object_or_404(SubjectiveQuestion, id=question_id)
    # QuestionKeywordMapping through 객체를 이용해 keyword + importance 함께 꺼내오기
    mappings = question.questionkeywordmapping_set.select_related('keyword')
    return render(request, 'question/user/subjective_question_detail.html', {
        'question': question,
        'mappings': mappings,
    })
