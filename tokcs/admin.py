from django.contrib import admin
from .models import Topic, Chapter, QuizQuestion, QuizChoice, UserAnswer

# Register your models here.
admin.site.register(Topic)
admin.site.register(Chapter)
admin.site.register(QuizQuestion)
admin.site.register(QuizChoice)
admin.site.register(UserAnswer)