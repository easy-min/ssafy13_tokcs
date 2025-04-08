# settings.py

# 1. 표준 라이브러리
from pathlib import Path
import os

# 2. 외부 패키지
from dotenv import load_dotenv

# 3. .env 로드
load_dotenv()

# 4. 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# 5. 환경 변수 설정
DEBUG = os.getenv('DEBUG') == 'True'
ENV = os.getenv('ENV', 'production')  # 기본값

# 6. 장고 앱 등록
INSTALLED_APPS = [
    # 기본 앱
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 내부 앱
    'tokcs.user',
    'tokcs.question',
    'tokcs.evaluation',
    'tokcs.study',
    'tokcs.stats',
    'tokcs.common',
]

# 7. 미들웨어 설정
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 8. 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 9. 데이터베이스 설정 : 일단 SQLite3 사용
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
