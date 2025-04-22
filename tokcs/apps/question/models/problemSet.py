# question/models/problemSet.py

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from datetime import date

class ProblemSet(models.Model):
    title = models.CharField(max_length=255, verbose_name="문제 세트 제목")
    description = models.TextField(blank=True, verbose_name="설명")
    
    # 문제 세트가 활성화되는 시작 날짜 (예: 시험 시작 날짜)
    scheduled_date = models.DateField(verbose_name="시작 날짜", help_text="문제 세트가 활성화될 날짜")
    # 문제 세트의 마감 날짜 (예: 시험 종료 날짜)
    close_date = models.DateField(verbose_name="마감 날짜", help_text="문제 세트가 더 이상 접근 불가능한 날짜")
    
    total_score = models.PositiveIntegerField(default=100, verbose_name="총점")
    # is_active: 현재 문제 세트가 활성화되어 있는지 표시.
    # scheduled_date가 지나고 close_date 이전이면 활성화된 상태로 관리.
    is_active = models.BooleanField(default=False, verbose_name="활성화 여부",
                                    help_text="시작 날짜가 지나고 마감 날짜 전이면 활성화됩니다.")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")

    def __str__(self):
        return self.title

    def check_and_update_activation(self):
        """
        문제 세트의 활성화 상태를 검사하고 업데이트합니다.
          - 시작 날짜(scheduled_date) <= 오늘 < 마감 날짜(close_date)인 경우: 활성화(is_active=True)
          - 오늘이 마감 날짜(close_date) 이상이면: 비활성화(is_active=False)
        이 메서드는 백그라운드 작업이나 뷰에서 호출할 수 있습니다.
        """
        today = date.today()
        if self.scheduled_date <= today < self.close_date:
            if not self.is_active:
                self.is_active = True
                self.save()
        else:
            if self.is_active:
                self.is_active = False
                self.save()

class ProblemSetQuestion(models.Model):
    problemset = models.ForeignKey(
        ProblemSet,
        on_delete=models.CASCADE,
        related_name="problems",
        verbose_name="문제 세트"
    )
    # GenericForeignKey를 사용하여 객관식/주관식 등 BaseQuestion 상속 모델들을 모두 참조 가능
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
