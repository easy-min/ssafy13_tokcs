from django.db import models

class Topic(models.Model):
    name = models.CharField(max_length=100, verbose_name="주제 이름")
    description = models.TextField(blank=True, verbose_name="설명")

    def __str__(self):
        return self.name
