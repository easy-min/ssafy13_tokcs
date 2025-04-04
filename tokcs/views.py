from decimal import Decimal
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .models import QuizQuestion, SubjectiveGrading, Topic, Chapter, DailyQuizPool, UserDailyQuiz, ObjectiveAnswer, SubjectiveAnswer, grade_single_answer, highlight_keywords
from .forms import QuizQuestionForm
import re
from datetime import datetime, timezone

@login_required
def profile(request):
    return render(request, 'user/profile.html')

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def mypage(request):
    my_questions = QuizQuestion.objects.filter(author=request.user).order_by('-created_at')
    objective_answers = ObjectiveAnswer.objects.filter(user=request.user).select_related('question').order_by('-submitted_at')
    subjective_answers = SubjectiveAnswer.objects.filter(user=request.user).select_related('question').order_by('-submitted_at')
    user_quizzes = UserDailyQuiz.objects.filter(user=request.user).order_by('-id')
    return render(request, 'user/mypage.html', {
        'my_questions': my_questions,
        'objective_answers': objective_answers,
        'subjective_answers': subjective_answers,
        'user_quizzes': user_quizzes,
    })

@login_required
def create_subjective_quiz(request):
    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            if question.chapter:
                question.topic = question.chapter.topic
            question.save()
            tail_texts = request.POST.getlist('tail_question_text[]')
            tail_answers = request.POST.getlist('tail_answer_text[]')
            tail_keywords = request.POST.getlist('tail_keywords[]')
            tail_explanations = request.POST.getlist('tail_explanation[]')
            for idx in range(len(tail_texts)):
                tail_question = QuizQuestion(
                    chapter=question.chapter,
                    topic=question.topic,
                    question_text=tail_texts[idx],
                    answer_text=tail_answers[idx],
                    keywords=tail_keywords[idx],
                    explanation=tail_explanations[idx],
                    question_type='subjective',
                    is_tail_question=True,
                    parent_question=question,
                    author=request.user,
                )
                tail_question.save()
            messages.success(request, "문제가 성공적으로 등록되었습니다.")
            return redirect('mypage')
        else:
            messages.error(request, "폼에 오류가 있습니다.")
    else:
        form = QuizQuestionForm()
    topics = Topic.objects.all()
    chapters = Chapter.objects.all()
    return render(request, 'quiz/user/create_subjective_quiz.html', {
        'form': form,
        'topics': topics,
        'chapters': chapters,
    })

@login_required
def quiz_start(request):
    today_quiz = DailyQuizPool.objects.order_by('-day_number').first()
    if not today_quiz:
        return render(request, 'quiz/no_quiz.html')
    user_quiz, created = UserDailyQuiz.objects.get_or_create(
        user=request.user,
        day_quiz=today_quiz
    )
    if created:
        assigned_questions = user_quiz.assigned_questions.all()
        random_questions = today_quiz.question_bank.exclude(
            id__in=assigned_questions.values('id')
        ).order_by('?')
        random_questions = random_questions[:today_quiz.num_questions_per_user]
        user_quiz.assigned_questions.set(random_questions)
    step = int(request.GET.get('step', 1))
    questions = user_quiz.assigned_questions.all().order_by('id')
    if request.method == 'POST':
        q_id = request.POST.get('question_id')
        answer_text = request.POST.get('answer_text')
        question = QuizQuestion.objects.get(id=q_id)
        SubjectiveAnswer.objects.create(user=request.user, question=question, answer_text=answer_text)
        step += 1
        if step > questions.count():
            answers = SubjectiveAnswer.objects.filter(
                user=request.user,
                question__in=user_quiz.assigned_questions.all()
            )
            total_score = 0
            for ans in answers:
                total_score += grade_single_answer(ans)
            final_score = round((total_score / (len(answers) * 100)) * 100, 2)
            user_quiz.total_score = final_score
            user_quiz.save()
            return redirect('mypage')
        # 리다이렉트 시 현재 경로(request.path)를 사용해 쿼리스트링을 붙입니다.
        return redirect(request.path + f'?step={step}')
    current_question = questions[step - 1] if step <= questions.count() else None
    return render(request, 'quiz/user/quiz_start.html', {
        'question': current_question,
        'step': step,
        'total': questions.count(),
        'user_quiz': user_quiz,
    })

@login_required
def quiz_result(request, day_quiz_id):
    user_quiz = UserDailyQuiz.objects.get(user=request.user, day_quiz_id=day_quiz_id)
    answers = SubjectiveAnswer.objects.filter(user=request.user, question__in=user_quiz.assigned_questions.all())
    return render(request, 'quiz/user/quiz_result.html', {
        'user_quiz': user_quiz,
        'answers': answers,
    })

@staff_member_required
def create_daily_quiz(request):
    topics = Topic.objects.all()
    chapters = Chapter.objects.all()
    if request.method == 'POST':
        selected_date = request.POST.get('quiz_date')
        if not selected_date:
            messages.error(request, "날짜를 선택해주세요.")
            return render(request, 'quiz/admin/create_daily_quiz.html', {
                'topics': topics,
                'chapters': chapters,
            })
        day_number = selected_date.replace('-', '')[2:]
        total_count = int(request.POST.get('total_count'))
        topic_ids = request.POST.getlist('topics')
        chapter_ids = request.POST.getlist('chapters')
        quiz_set = DailyQuizPool.objects.create(
            day_number=day_number,
            title=f"Day {day_number} 문제 세트",
            num_questions_per_user=total_count
        )
        quiz_set.topics.set(topic_ids)
        quiz_set.chapters.set(chapter_ids)
        question_pool = QuizQuestion.objects.filter(topic__in=topic_ids, chapter__in=chapter_ids).order_by('?')
        quiz_set.question_bank.set(question_pool)
        quiz_set.save()
        messages.success(request, f"Day {day_number} 문제 세트가 생성되었습니다.")
        return redirect('daily_quiz_list')
    return render(request, 'quiz/admin/create_daily_quiz.html', {
        'topics': topics,
        'chapters': chapters,
    })

@staff_member_required
def daily_quiz_list(request):
    quiz_sets = DailyQuizPool.objects.order_by('-day_number')
    return render(request, 'quiz/admin/daily_quiz_list.html', {
        'quiz_sets': quiz_sets
    })

def grade_single_answer(answer_obj):
    answer_text = answer_obj.answer_text
    keywords = answer_obj.question.keywords.split(",") if answer_obj.question.keywords else []
    total_keywords = len(keywords)
    matched = sum(1 for kw in keywords if kw.strip() in answer_text)
    missed = total_keywords - matched
    if missed == 0:
        score = 100
    elif missed == 1:
        score = 70
    elif missed == 2:
        score = 40
    else:
        score = 0
    answer_obj.answer_text = highlight_keywords(answer_text, keywords)
    answer_obj.score = score
    answer_obj.graded = True
    answer_obj.save()
    matched_list = [kw.strip() for kw in keywords if kw.strip() in answer_text]
    missed_list = [kw.strip() for kw in keywords if kw.strip() not in answer_text]
    SubjectiveGrading.objects.update_or_create(
        answer=answer_obj,
        defaults={
            'auto_keywords_matched': ','.join(matched_list),
            'auto_keywords_missed': ','.join(missed_list),
            'auto_score': score,
        }
    )
    return score

@staff_member_required
def grade_user_answers(request, day_quiz_id):
    user_quiz = UserDailyQuiz.objects.get(day_quiz_id=day_quiz_id)
    answers = SubjectiveAnswer.objects.filter(question__in=user_quiz.assigned_questions.all(), user=user_quiz.user)
    total_score = 0
    for ans in answers:
        total_score += grade_single_answer(ans)
    final_score = round((total_score / (len(answers) * 100)) * 100, 2)
    user_quiz.total_score = final_score
    user_quiz.save()
    messages.success(request, f"채점 완료! 최종 점수: {final_score}점")
    return redirect('daily_quiz_list')

@login_required
@staff_member_required
def correct_subjective_answer(request, answer_id):
    answer = get_object_or_404(SubjectiveAnswer, pk=answer_id)
    grading = answer.grading
    if request.method == 'POST':
        new_score = Decimal(request.POST['manual_score'])
        memo = request.POST.get('memo', '')
        grading.manual_score = new_score
        grading.manually_corrected = True
        grading.corrected_by = request.user
        grading.corrected_at = timezone.now()
        grading.correction_memo = memo
        grading.save()
        answer.score = new_score
        answer.save()
        return redirect('grading_review_list')
    return render(request, 'grading/correct_answer.html', {
        'answer': answer,
        'grading': grading,
    })

@login_required
def quiz_result(request, day_quiz_id):
    user_quiz = UserDailyQuiz.objects.get(user=request.user, day_quiz_id=day_quiz_id)
    answers = SubjectiveAnswer.objects.filter(
        user=request.user,
        question__in=user_quiz.assigned_questions.all()
    ).select_related('question', 'grading')
    
    # (옵션) 전체 점수를 다시 계산할 수 있음.
    total_possible = answers.count() * 100
    total_score = sum(answer.final_score or 0 for answer in answers)
    final_percentage = round((total_score / total_possible) * 100, 2) if total_possible else 0

    return render(request, 'quiz/user/quiz_result.html', {
        'user_quiz': user_quiz,
        'answers': answers,
        'final_percentage': final_percentage,
    })
