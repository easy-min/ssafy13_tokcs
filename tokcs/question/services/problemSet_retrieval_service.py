from datetime import date
from django.db.models import Prefetch
from tokcs.question.models.problemSet import ProblemSet, ProblemSetQuestion
from tokcs.question.models.choice import ObjectiveAnswer, SubjectiveAnswer
from django.contrib.auth import get_user_model

User = get_user_model()

def get_active_problem_sets():
    today = date.today()
    return ProblemSet.objects.filter(scheduled_date__lte=today, close_date__gt=today, is_active=True)

def get_problem_set_details(problem_set_id):
    try:
        problem_set = ProblemSet.objects.get(id=problem_set_id)
    except ProblemSet.DoesNotExist:
        return None
    ps_questions = problem_set.problems.all().order_by('order')
    details = {
        'title': problem_set.title,
        'description': problem_set.description,
        'scheduled_date': problem_set.scheduled_date,
        'close_date': problem_set.close_date,
        'total_score': problem_set.total_score,
        'is_active': problem_set.is_active,
        'created_at': problem_set.created_at,
        'questions': list(ps_questions),
    }
    return details

def get_user_recent_submissions(user, limit=5):
    from django.db.models import Q
    objective_qs = ObjectiveAnswer.objects.filter(user=user).select_related('question').order_by('-created_at')[:limit]
    subjective_qs = SubjectiveAnswer.objects.filter(user=user).select_related('question').order_by('-created_at')[:limit]
    submissions = list(objective_qs) + list(subjective_qs)
    submissions.sort(key=lambda x: x.created_at, reverse=True)
    return submissions[:limit]
