# question/models/problemSet.py

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class ProblemSet(models.Model):
    title = models.CharField(max_length=255, verbose_name="문제 세트 제목")
    description = models.TextField(blank=True, verbose_name="설명")
    total_score = models.PositiveIntegerField(default=100, verbose_name="총점")
    day = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="DAY 번호",
        help_text="예: 250327 형식의 문자열"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")

    def __str__(self):
        return self.title

class ProblemSetQuestion(models.Model):
    problemset = models.ForeignKey(
        ProblemSet,
        on_delete=models.CASCADE,
        related_name="problems",
        verbose_name="문제 세트"
    )
    # GenericForeignKey를 사용하여 ObjectiveQuestion, SubjectiveQuestion 등 BaseQuestion 상속 모델 모두 참조 가능
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    question = GenericForeignKey('content_type', 'object_id')
    
    order = models.PositiveIntegerField(default=0, verbose_name="순서")

    class Meta:
        verbose_name = "문제 세트 문제"
        verbose_name_plural = "문제 세트 문제들"
        ordering = ['order']

    def __str__(self):
        return f"{self.problemset.title} - 문제 {self.order}"
