from django.contrib import admin, messages
from .models import (
    Topic, Chapter, QuizQuestion, QuizChoice,
    SubjectiveAnswer, SubjectiveGrading,
    DailyQuizPool, UserDailyQuiz, grade_single_answer
)

admin.site.register(Topic)
admin.site.register(Chapter)
admin.site.register(QuizQuestion)
admin.site.register(QuizChoice)
admin.site.register(DailyQuizPool)
# UserDailyQuiz는 데코레이터 방식으로 등록합니다.
# admin.site.register(UserDailyQuiz)

@admin.register(SubjectiveAnswer)
class SubjectiveAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'score', 'graded', 'submitted_at')
    list_filter = ('graded',)
    search_fields = ('user__username', 'question__code')

@admin.register(SubjectiveGrading)
class SubjectiveGradingAdmin(admin.ModelAdmin):
    list_display = (
        'answer', 'auto_score', 'manual_score',
        'manually_corrected', 'corrected_by', 'corrected_at'
    )
    readonly_fields = (
        'answer', 'auto_keywords_matched', 'auto_keywords_missed', 'auto_score'
    )
    list_filter = ('manually_corrected',)
    search_fields = ('answer__question__code', 'answer__user__username')
    ordering = ('-corrected_at',)

    def has_add_permission(self, request):
        # 새 레코드 추가를 막아 IntegrityError를 방지합니다.
        return False

@admin.register(UserDailyQuiz)
class UserDailyQuizAdmin(admin.ModelAdmin):
    list_display = ('user', 'day_quiz', 'total_score', 'assigned_at')
    actions = ['regrade_quiz']

    def regrade_quiz(self, request, queryset):
        count = 0
        for quiz in queryset:
            # 해당 퀴즈 세트의 주관식 답안을 가져옵니다.
            answers = SubjectiveAnswer.objects.filter(
                user=quiz.user,
                question__in=quiz.assigned_questions.all()
            )
            total_score = 0
            for ans in answers:
                # 각 답안을 채점하는 함수 호출
                total_score += grade_single_answer(ans)
            if answers:
                # 전체 점수를 백분율로 계산 (각 문제 만점 100점 기준)
                final_score = round((total_score / (len(answers) * 100)) * 100, 2)
            else:
                final_score = 0
            quiz.total_score = final_score
            quiz.save()
            count += 1
        self.message_user(request, f"{count}개의 퀴즈 세트 채점이 다시 완료되었습니다.", messages.SUCCESS)

    regrade_quiz.short_description = "채점 다시하기 (선택한 퀴즈 세트)"
