from django.db import models
from django.conf import settings
from django.utils import timezone

from question.models.problemSet import ProblemSet

class ExamSession(models.Model):
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problemset   = models.ForeignKey(ProblemSet,         on_delete=models.CASCADE)
    start_time   = models.DateTimeField(auto_now_add=True)
    end_time     = models.DateTimeField(null=True, blank=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'problemset')
        ordering        = ['-start_time']

    @property
    def time_left(self):
        elapsed = (timezone.now() - self.start_time).seconds
        return max(3600 - elapsed, 0)  # 1시간 제한

    @property
    def is_active(self):
        return not self.is_submitted and self.time_left > 0
