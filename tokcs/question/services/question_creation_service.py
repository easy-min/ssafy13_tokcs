from django.core.exceptions import ValidationError
from tokcs.question.models.chapter import Chapter
from tokcs.question.models.question import (
    ObjectiveQuestion,
    SubjectiveQuestion,
    Choice
)
from django.contrib.auth import get_user_model

User = get_user_model()

def create_objective_question(user, data):
    # 관리자 권한 검사 제거
    try:
        chapter = Chapter.objects.get(id=data['chapter_id'])
    except Chapter.DoesNotExist:
        raise ValidationError("유효한 Chapter가 아닙니다.")
    question = ObjectiveQuestion.objects.create(
        chapter=chapter,
        question_type="MCQ",
        content=data['content'],
        explanation=data.get('explanation', ""),
        score=data.get('score', 5)
    )
    choices_data = data.get('choices', [])
    if not choices_data:
        raise ValidationError("객관식 문제는 적어도 하나의 선택지가 필요합니다.")
    for choice_data in choices_data:
        Choice.objects.create(
            question=question,
            content=choice_data.get('content'),
            is_correct=choice_data.get('is_correct', False)
        )
    return question

def create_subjective_question(user, data):
    # 관리자 권한 검사 제거
    try:
        chapter = Chapter.objects.get(id=data['chapter_id'])
    except Chapter.DoesNotExist:
        raise ValidationError("유효한 Chapter가 아닙니다.")
    question = SubjectiveQuestion.objects.create(
        chapter=chapter,
        question_type="SA",
        content=data['content'],
        explanation=data.get('explanation', ""),
        score=data.get('score', 5)
    )
    keyword_ids = data.get('keyword_ids', [])
    if keyword_ids:
        question.keywords.set(keyword_ids)
    return question

def create_multiple_questions(user, questions_data):
    created_questions = []
    errors = []
    for idx, data in enumerate(questions_data):
        q_type = data.get('question_type')
        try:
            if q_type == 'MCQ':
                question = create_objective_question(user, data)
            elif q_type == 'SA':
                question = create_subjective_question(user, data)
            else:
                raise ValidationError(f"문제 {idx}: 유효하지 않은 문제 유형입니다: {q_type}")
            created_questions.append(question)
        except Exception as ex:
            errors.append({"index": idx, "error": str(ex)})
    if errors:
        raise ValidationError(errors)
    return created_questions
