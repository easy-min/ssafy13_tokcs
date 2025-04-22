from django.db import models
from django.contrib.auth import get_user_model
from ..models.question import ObjectiveQuestion, Choice, SubjectiveQuestion

User = get_user_model() # 항상 현재 설정에 따른 사용자 모델을 반환

class ObjectiveAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")
    question = models.ForeignKey(ObjectiveQuestion, on_delete=models.CASCADE, verbose_name="문제")
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, verbose_name="선택된 보기")
    score = models.PositiveIntegerField(default=0, verbose_name="채점 점수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="제출일")
    def __str__(self):
        return f"{self.user} - {self.question} -> {self.selected_choice}"

class SubjectiveAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")
    question = models.ForeignKey(SubjectiveQuestion, on_delete=models.CASCADE, verbose_name="문제")
    answer_text = models.TextField(verbose_name="답안 내용")
    score = models.IntegerField(default=0, verbose_name="채점 점수")
    matched_keywords = models.JSONField(default=list, verbose_name="매칭된 키워드")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="제출일")
    
    def __str__(self):
        return f"{self.user} - {self.question}"
