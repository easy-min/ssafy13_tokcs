from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..forms.subjective_question_forms import SubjectiveQuestionForm
from ..services.question_creation_service import create_subjective_question
from ..models.topic import Topic
from ..models.chapter import Chapter
from ..models.question import Keyword  # Keyword 모델 임포트
from ..models.question import SubjectiveQuestion

@login_required
def create_subjective_question_view(request):
    topics = Topic.objects.all()
    chapters = Chapter.objects.all()
    
    if request.method == 'POST':
        form = SubjectiveQuestionForm(request.POST)
        # 먼저 폼 유효성 검사를 실행 (chapter, content, 등은 여기서 처리됨)
        if form.is_valid():
            # 템플릿에서 키워드 텍스트들을 직접 가져옴
            keyword_texts = request.POST.getlist('keywords[]')
            if not keyword_texts or len([k for k in keyword_texts if k.strip()]) == 0:
                form.add_error(None, "최소 하나 이상의 키워드를 입력해야 합니다.")
                return render(request, 'question/user/create_subjective_question.html', {
                    'form': form,
                    'topics': topics,
                    'chapters': chapters,
                })

            # 키워드 텍스트를 처리하여 Keyword 인스턴스의 ID 리스트 만들기
            keyword_ids = []
            for kw_text in keyword_texts:
                kw_text = kw_text.strip()
                if kw_text:
                    # 이미 존재하는 Keyword가 있다면 가져오거나, 없으면 생성
                    keyword_obj, created = Keyword.objects.get_or_create(word=kw_text)
                    keyword_ids.append(keyword_obj.id)
            
            # 폼 데이터를 활용하여 question_data 구성 (기존과 동일)
            question_data = {
                "chapter_id": form.cleaned_data['chapter'].id,
                "content": form.cleaned_data['content'],
                "explanation": form.cleaned_data.get('explanation', ""),
                "score": form.cleaned_data.get('score', 5),
                "question_type": "SA",
                "keyword_ids": keyword_ids
            }
            question = create_subjective_question(request.user, question_data)
            
            submit_type = request.POST.get('submit_type', 'finish')
            if submit_type == 'continue':
                return redirect('create_subjective_question')  # 계속 출제하면 같은 페이지 리디렉션
            else:
                return redirect('subjective_question_detail', question_id=question.id)
        else:
            return render(request, 'question/user/create_subjective_question.html', {
                'form': form,
                'topics': topics,
                'chapters': chapters,
            })
    else:
        form = SubjectiveQuestionForm()
        return render(request, 'question/user/create_subjective_question.html', {
            'form': form,
            'topics': topics,
            'chapters': chapters,
        })

@login_required
def subjective_question_detail_view(request, question_id):
    question = get_object_or_404(SubjectiveQuestion, id=question_id)
    return render(request, 'question/user/subjective_question_detail.html', {
        'question': question,
    })