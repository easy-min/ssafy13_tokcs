from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from datetime import date
from django.conf import settings

class ProblemSet(models.Model):
    title           = models.CharField(max_length=255, verbose_name="문제 세트 제목")
    description     = models.TextField(blank=True, verbose_name="설명")
    scheduled_date  = models.DateField(verbose_name="시작 날짜")
    close_date      = models.DateField(verbose_name="마감 날짜")
    total_score     = models.PositiveIntegerField(default=100, verbose_name="총점")
    pass_threshold  = models.PositiveIntegerField(default=70, verbose_name="합격 기준(%)",
                                                 help_text="예: 70점 이상 합격")
    is_active       = models.BooleanField(default=False, verbose_name="활성화 여부")
    created_at      = models.DateTimeField(auto_now_add=True, verbose_name="생성일")

    class Meta:
        verbose_name        = "문제 세트"
        verbose_name_plural = "문제 세트들"
        ordering            = ['-scheduled_date']
        indexes             = [
            models.Index(fields=["scheduled_date"]),
            models.Index(fields=["close_date"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.title
    # active라는 가상(읽기 전용) 속성을 제공
    @property
    def active(self):
        today = date.today()
        return self.scheduled_date <= today < self.close_date

class ProblemSetQuestion(models.Model):
    problemset   = models.ForeignKey(ProblemSet, on_delete=models.CASCADE,
                                     related_name="problems", verbose_name="문제 세트")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id    = models.PositiveIntegerField()
    question     = GenericForeignKey('content_type', 'object_id')
    order        = models.PositiveIntegerField(default=0, verbose_name="순서")

    class Meta:
        verbose_name        = "문제 세트 내 문제"
        verbose_name_plural = "문제 세트 내 문제들"
        ordering            = ['order']
        unique_together     = [('problemset', 'order')]
