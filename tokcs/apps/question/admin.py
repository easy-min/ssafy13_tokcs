# question/admin.py

from django.contrib import admin

# 만약 Topic과 Chapter 모델이 별도의 파일에 있다면 경로에 맞게 import 합니다.
# 예시: question/models/topic.py, question/models/chapter.py
from .models.topic import Topic
from .models.chapter import Chapter

# 다른 모델들은 models 패키지(또는 파일) 내에 있다면 아래와 같이 import합니다.
from .models.question import (
    ObjectiveQuestion,
    Choice,
    SubjectiveQuestion,
    QuestionKeywordMapping,
    Keyword,
)

admin.site.register(Topic)
admin.site.register(Chapter)
admin.site.register(ObjectiveQuestion)
admin.site.register(Choice)
admin.site.register(SubjectiveQuestion)
admin.site.register(QuestionKeywordMapping)
admin.site.register(Keyword)
