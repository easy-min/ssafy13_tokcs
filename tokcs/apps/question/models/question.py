from django.db import models
from ..models.topic import Topic
from ..models.chapter import Chapter

class BaseQuestion(models.Model):
    QUESTION_TYPES = [
        ('MCQ', '객관식'),
        ('SA', '주관식'),
    ]
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, verbose_name="단원")  # 1:N 관계
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, verbose_name="문제 유형")
    content = models.TextField(verbose_name="문제 내용")
    explanation = models.TextField(blank=True, verbose_name="해설")
    score = models.PositiveIntegerField(null=True, blank=True, verbose_name="배점")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.content[:30]}"

class ObjectiveQuestion(BaseQuestion):
    class Meta:
        verbose_name = "객관식 문제"
        verbose_name_plural = "객관식 문제들"

class Choice(models.Model):
    question = models.ForeignKey(ObjectiveQuestion, on_delete=models.CASCADE, related_name='choices')
    content = models.CharField(max_length=200, verbose_name="보기 내용")
    is_correct = models.BooleanField(default=False, verbose_name="정답 여부")
    
    class Meta:
        verbose_name = "객관식 보기"
        verbose_name_plural = "객관식 보기들"
    
    def __str__(self):
        return f"{self.content} ({'정답' if self.is_correct else '오답'})"

class SubjectiveQuestion(BaseQuestion):
    # 대상 모델을 문자열 'Keyword'로 지정하여 나중에 참조하도록 함
    keywords = models.ManyToManyField('Keyword', through='QuestionKeywordMapping', verbose_name="채점용 키워드")
    
    class Meta:
        verbose_name = "주관식 문제"
        verbose_name_plural = "주관식 문제들"

class QuestionKeywordMapping(models.Model):
    question = models.ForeignKey(SubjectiveQuestion, on_delete=models.CASCADE)
    # 역시 대상 모델을 문자열 'Keyword'로 지정
    keyword = models.ForeignKey('Keyword', on_delete=models.CASCADE)
    importance = models.IntegerField(default=1, verbose_name="중요도")  # 나중에 가중치 기반 채점용
    
    class Meta:
        verbose_name = "문제-키워드 매핑"
        unique_together = ('question', 'keyword')

# PostgreSQL 기반: JSONField를 사용하려면 PostgreSQL 권장
class Keyword(models.Model):
    word = models.CharField(max_length=100, unique=True, verbose_name="대표 키워드")
    synonyms = models.JSONField(default=list, verbose_name="동의어 목록")  # 예: ["network", "LAN", "네 트워크"]
    
    def all_variants(self):
        return [self.word] + self.synonyms
    
    def __str__(self):
        return self.word
