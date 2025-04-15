from django.contrib import admin
from django.urls import path, include
from tokcs.user.views import homepage_view, signup_view  # 여기에서 homepage_view와 signup_view 임포트
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 로그인이 된 사용자는 홈페이지로 리다이렉트
    path('', homepage_view, name='home'),
    path('signup/', signup_view, name='signup'),
    # 로그인 URL (인증되지 않은 경우)
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html', redirect_authenticated_user=True), name='login'),
    path('admin/', admin.site.urls),
    path('question/', include('tokcs.question.urls')),
]
