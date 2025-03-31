from django.db import models
from django.contrib.auth.models import User
import re

def get_default_topic():
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
        default=get_default_topic
    )
    name = models.CharField(max_length=100, verbose_name="단원 이름")
    order = models.IntegerField(default=0, verbose_name="순서")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    
    def __str__(self):
        return f"[{self.topic.name}] {self.name}"

def highlight_keywords(answer_text, keywords):
    for kw in keywords:
        if kw.strip():
            answer_text = re.sub(f'({re.escape(kw.strip())})', r'<span style="color:blue; font-weight:bold;">\1</span>', answer_text)
    return answer_text


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
    
    @property
    def final_score(self):
        if hasattr(self, 'grading'):
            return self.grading.final_score()
        return self.score

class SubjectiveGrading(models.Model):
    answer = models.OneToOneField(SubjectiveAnswer, on_delete=models.CASCADE, related_name='grading')
    auto_keywords_matched = models.TextField(blank=True, help_text="자동 채점 시 매칭된 키워드")
    auto_keywords_missed = models.TextField(blank=True, help_text="자동 채점 시 누락된 키워드")
    auto_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    manually_corrected = models.BooleanField(default=False)
    manual_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    corrected_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='manual_graders')
    corrected_at = models.DateTimeField(null=True, blank=True)
    correction_memo = models.TextField(blank=True)

    def final_score(self):
        return self.manual_score if self.manually_corrected else self.auto_score


def auto_grade_subjective_answer(answer: SubjectiveAnswer):
    expected_keywords = [kw.strip() for kw in answer.question.keywords.split(',') if kw.strip()]
    user_text = answer.answer_text.lower()
    matched_list = [kw.strip() for kw in expected_keywords if kw.lower() in user_text]
    missed_list = [kw.strip() for kw in expected_keywords if kw.lower() not in user_text]
    missed_count = len(missed_list)
    if missed_count == 0:
        score = 100
    elif missed_count == 1:
        score = 70
    elif missed_count == 2:
        score = 40
    else:
        score = 0
    highlighted = highlight_keywords(answer.answer_text, expected_keywords)
    answer.answer_text = highlighted
    answer.score = score
    answer.graded = True
    answer.save()
    SubjectiveGrading.objects.update_or_create(
        answer=answer,
        defaults={
            'auto_keywords_matched': ','.join(matched_list),
            'auto_keywords_missed': ','.join(missed_list),
            'auto_score': score,
        }
    )
    return score

class DailyQuizPool(models.Model):
    day_number = models.IntegerField(unique=True)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    topics = models.ManyToManyField('Topic', blank=True)
    chapters = models.ManyToManyField('Chapter', blank=True)
    question_bank = models.ManyToManyField('QuizQuestion', blank=True)
    num_questions_per_user = models.IntegerField(default=20)
    
    def __str__(self):
        return f"Day {self.day_number} - {self.title}"

class UserDailyQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day_quiz = models.ForeignKey(DailyQuizPool, on_delete=models.CASCADE)
    assigned_questions = models.ManyToManyField('QuizQuestion')
    assigned_at = models.DateTimeField(auto_now_add=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - Day {self.day_quiz.day_number}"

def grade_single_answer(answer_obj):
    """
    주관식 답안을 평가하여 점수를 산출하고, SubjectiveGrading 레코드를 생성/업데이트 합니다.
    """
    answer_text = answer_obj.answer_text
    keywords = answer_obj.question.keywords.split(",") if answer_obj.question.keywords else []
    total_keywords = len(keywords)
    matched = sum(1 for kw in keywords if kw.strip() in answer_text)
    missed = total_keywords - matched

    if missed == 0:
        score = 100
    elif missed == 1:
        score = 30
    elif missed == 2:
        score = 10
    else:
        score = 0

    answer_obj.answer_text = highlight_keywords(answer_text, keywords)
    answer_obj.score = score
    answer_obj.graded = True
    answer_obj.save()

    matched_list = [kw.strip() for kw in keywords if kw.strip() in answer_text]
    missed_list = [kw.strip() for kw in keywords if kw.strip() not in answer_text]

    SubjectiveGrading.objects.update_or_create(
        answer=answer_obj,
        defaults={
            'auto_keywords_matched': ','.join(matched_list),
            'auto_keywords_missed': ','.join(missed_list),
            'auto_score': score,
        }
    )
    return score
