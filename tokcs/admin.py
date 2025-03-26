from django.contrib import admin
from .models import Topic, Chapter, QuizQuestion, QuizChoice, SubjectiveAnswer, DailyQuizPool, UserDailyQuiz

# Register your models here.
admin.site.register(Topic)
admin.site.register(Chapter)
admin.site.register(QuizQuestion)
admin.site.register(QuizChoice)
admin.site.register(SubjectiveAnswer)  # SubjectiveAnswer 등록
admin.site.register(DailyQuizPool)
admin.site.register(UserDailyQuiz)