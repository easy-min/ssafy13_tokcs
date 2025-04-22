# tokcs/user/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # 회원가입 후 로그인 페이지로 리다이렉트
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def homepage_view(request):
    # 최근 문제 셋, 최근 활동 등 필요한 데이터를 context로 전달합니다.
    # 예시로 빈 리스트를 넘겨주고 있습니다. 실제 구현 시 필요한 데이터를 조회하세요.
    context = {
        'recent_problem_sets': [],
        'recent_activities': [],
    }
    return render(request, 'user/homepage.html', context)

