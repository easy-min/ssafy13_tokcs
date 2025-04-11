from django.db import models
from quiz.models.topic import Topic

def get_default_topic():
    return Topic.objects.first() #topic 한 개 이상 있어야 오류 안남

class Chapter(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="chapters",
        verbose_name="주제",
        default=get_default_topic
    )
    name = models.CharField(max_length=100, verbose_name="단원 이름")
    order = models.IntegerField(default=0, verbose_name="순서")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    
    def __str__(self):
        return f"[{self.topic.name}] {self.name}"
