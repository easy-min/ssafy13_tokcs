# tokcs/models.py
from django.db import models
from django.contrib.auth.models import User

def get_default_topic():
    # 주의: 이 함수는 마이그레이션 시 기본 Topic의 ID를 반환합니다.
    # 예를 들어, "컴퓨터구조와운영체제" Topic이 미리 만들어져 있고 그 ID가 1이라고 가정합니다.
    return 1

class Topic(models.Model):
    """
    다양한 주제를 관리하는 모델입니다.
    예: "컴퓨터구조와운영체제", "네트워크", "SQL", "머신러닝" 등
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="주제")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    
    def __str__(self):
        return self.name

class Chapter(models.Model):
    """
    각 주제(Topic)에 속한 단원을 관리하는 모델입니다.
    예: "1회차: (1장) 컴퓨터 구조 시작하기", "2회차: (4장) CPU의 작동 원리" 등
    """
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="chapters",
        verbose_name="주제",
        default=get_default_topic  # 기본 Topic ID를 1로 설정 (Topic with ID 1은 "컴퓨터구조와운영체제"여야 함)
    )
    name = models.CharField(max_length=100, verbose_name="단원 이름")
    order = models.IntegerField(default=0, verbose_name="순서")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    
    def __str__(self):
        return f"[{self.topic.name}] {self.name}"

# 나머지 모델은 그대로 유지합니다.
class QuizQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('objective', '객관식'),
        ('subjective', '주관식'),
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name="문제 코드")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자", null=True, blank=True)
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="주제"
    )
    # 문제를 단원과 연결합니다.
    chapter = models.ForeignKey(
        Chapter,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="단원"
    )
    
    question_text = models.TextField(verbose_name="질문 내용")
    answer_text = models.TextField(
        verbose_name="모범 답안", blank=True,
        help_text="주관식 문제일 경우 모범 답안을 입력합니다."
    )
    keywords = models.TextField(
        verbose_name="주요 키워드", blank=True,
        help_text="쉼표(,)로 구분하여 입력"
    )
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        verbose_name="문제 유형"
    )
    is_tail_question = models.BooleanField(default=False, verbose_name="꼬리 질문 여부")
    
    parent_question = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='child_questions',
        verbose_name="부모 질문"
    )
    
    explanation = models.TextField(verbose_name="해설", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    
    def __str__(self):
        return f"{self.code} - {self.question_text[:30]}..."
    
    def save(self, *args, **kwargs):
        if not self.code:
            if self.is_tail_question and self.parent_question:
                # 꼬리 질문 코드 생성
                siblings = QuizQuestion.objects.filter(
                    parent_question=self.parent_question, is_tail_question=True
                )
                if siblings.exists():
                    last_num = max([
                        int(sibling.code.split('-')[-1]) 
                        for sibling in siblings 
                        if '-' in sibling.code and sibling.code.split('-')[-1].isdigit()
                    ] or [0])
                else:
                    last_num = 0
                self.code = f"{self.parent_question.code}-{last_num + 1}"
            else:
                # 일반 문제 코드 생성
                if self.chapter and self.chapter.topic:
                    prefix = self.chapter.topic.name[:2].upper()
                else:
                    prefix = "XX"
                last_question = QuizQuestion.objects.filter(
                    is_tail_question=False, chapter=self.chapter
                ).order_by('id').last()

                if last_question and last_question.code.startswith(prefix):
                    try:
                        last_number = int(last_question.code.replace(prefix, ""))
                    except ValueError:
                        last_number = 0
                else:
                    last_number = 0
                self.code = f"{prefix}{last_number + 1:03d}"

        # 중복 방지 루프
        counter = 1
        original_code = self.code
        while QuizQuestion.objects.filter(code=self.code).exists():
            self.code = f"{original_code}-{counter}"
            counter += 1

        super().save(*args, **kwargs)


class QuizChoice(models.Model):
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name="문제"
    )
    choice_text = models.CharField(max_length=200, verbose_name="선택지 내용")
    is_correct = models.BooleanField(default=False, verbose_name="정답 여부")
    
    def __str__(self):
        return f"{self.question.code} - {self.choice_text}"

class ObjectiveAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(QuizChoice, on_delete=models.SET_NULL, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

class SubjectiveAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    graded = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.code}"

class DailyQuizPool(models.Model):
    day_number = models.IntegerField(unique=True)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    topics = models.ManyToManyField('Topic', blank=True)
    chapters = models.ManyToManyField('Chapter', blank=True)
    question_bank = models.ManyToManyField('QuizQuestion', blank=True)  # 문제은행
    num_questions_per_user = models.IntegerField(default=20)  # 유저당 몇 개 출제

    def __str__(self):
        return f"Day {self.day_number} - {self.title}"


class UserDailyQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day_quiz = models.ForeignKey(DailyQuizPool, on_delete=models.CASCADE)
    assigned_questions = models.ManyToManyField('QuizQuestion')
    assigned_at = models.DateTimeField(auto_now_add=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # 추가된 필드
    def __str__(self):
        return f"{self.user.username} - Day {self.day_quiz.day_number}"
