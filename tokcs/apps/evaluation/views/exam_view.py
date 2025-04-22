from django.shortcuts               import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from .services import start_exam, get_exam_questions, submit_exam, grade_exam
from .models   import ExamSession

def is_admin(user):
    return user.is_staff

@login_required
def exam_start_view(request, ps_id):
    session = start_exam(request.user, ps_id)
    return redirect('exam_take', session_id=session.id)

@login_required
def exam_take_view(request, session_id):
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    if request.method == 'POST':
        submit_exam(session, request.POST)
        return redirect('exam_result', session_id=session.id)

    questions = get_exam_questions(session)
    return render(request, 'evaluation/exam_take.html', {
        'session':   session,
        'questions': questions,
    })

@login_required
def exam_result_view(request, session_id):
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    score   = grade_exam(session)
    return render(request, 'evaluation/exam_result.html', {
        'session': session,
        'score':   score,
    })
