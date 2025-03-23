# tokcs/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import QuizQuestionForm
from .models import QuizQuestion, Topic, Chapter
from django.http import HttpResponse

def create_question(request):
    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            # 부모 문제 저장 (폼 데이터 기반, 문제 코드 자동 생성 로직은 모델의 save()에서 처리)
            question = form.save(commit=False)
            question.save()
            
            # 꼬리 질문 데이터 처리: 배열 형태로 전송된 꼬리 질문 관련 필드를 순회
            tail_texts = request.POST.getlist('tail_question_text[]')
            tail_answers = request.POST.getlist('tail_answer_text[]')
            tail_keywords = request.POST.getlist('tail_keywords[]')
            tail_explanations = request.POST.getlist('tail_explanation[]')
            
            for idx in range(len(tail_texts)):
                tail_question = QuizQuestion(
                    chapter=question.chapter,        # 부모와 동일한 단원
                    topic=question.topic,            # 부모와 동일한 주제 (만약 ModelForm에서 topic 필드를 사용 중이라면)
                    question_text=tail_texts[idx],
                    answer_text=tail_answers[idx],
                    keywords=tail_keywords[idx],
                    explanation=tail_explanations[idx],
                    question_type='subjective',
                    is_tail_question=True,
                    parent_question=question,
                )
                tail_question.save()
            
            messages.success(request, "문제가 성공적으로 등록되었습니다.")
            return redirect('home')
        else:
            messages.error(request, "폼에 오류가 있습니다. 다시 시도해주세요.")
    else:
        form = QuizQuestionForm()
    
    # 템플릿에서 사용할 Topic, Chapter 목록을 컨텍스트로 전달
    topics = Topic.objects.all()
    chapters = Chapter.objects.all()
    return render(request, 'questions/subjective/create_subjective_question.html', {
        'form': form,
        'topics': topics,
        'chapters': chapters,
    })
def home(request):
    return HttpResponse("hello, this is toks home!")


# tokcs/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # 회원가입 성공 후 로그인 페이지로 이동
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
