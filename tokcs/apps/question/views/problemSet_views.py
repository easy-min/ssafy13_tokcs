from django.shortcuts            import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from question.forms.problemset_forms import ProblemSetForm
from question.services.problemset_service import create_random_problem_set

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def create_problem_set_view(request):
    if request.method == 'POST':
        form = ProblemSetForm(request.POST)
        if form.is_valid():
            ps, psqs = create_random_problem_set(request.user, form.cleaned_data)
            # 생성 직후 미리 보기(=detail)로 이동
            return redirect('problem_set_detail', ps_id=ps.id)
    else:
        form = ProblemSetForm()
    return render(request, 'problemset/create_random_problem_set.html', {
        'form': form
    })

@login_required
@user_passes_test(is_admin)
def problem_set_detail_view(request, ps_id):
    from question.services.problemset_retrieval_service import get_problem_set_details
    details = get_problem_set_details(ps_id)
    return render(request, 'problemset/problem_set_detail.html', {
        'problem_set': details
    })
@login_required
@user_passes_test(is_admin)
def problem_set_preview_view(request, ps_id):
    try:
        preview = get_problem_set_preview(ps_id)
    except Http404 as e:
        return render(request, 'problemset/preview.html', {
            'error': str(e)
        }, status=404)

    return render(request, 'problemset/preview.html', {
        'problemset': preview['problemset'],
        'questions':  preview['questions'],
    })
