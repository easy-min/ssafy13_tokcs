from django.db import models
from django.utils import timezone

from .exam_model import ExamSession
from question.models.question import ObjectiveQuestion, SubjectiveQuestion
from question.models.question import Choice

class ObjectiveAnswer(models.Model):
    session      = models.ForeignKey(ExamSession,    on_delete=models.CASCADE)
    question     = models.ForeignKey(ObjectiveQuestion, on_delete=models.CASCADE)
    choice       = models.ForeignKey(Choice,         on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('session', 'question')

class SubjectiveAnswer(models.Model):
    session      = models.ForeignKey(ExamSession,     on_delete=models.CASCADE)
    question     = models.ForeignKey(SubjectiveQuestion, on_delete=models.CASCADE)
    answer_text  = models.TextField()
    submitted_at = models.DateTimeField(auto_now=True)
    score        = models.FloatField(default=0)

    class Meta:
        unique_together = ('session', 'question')
