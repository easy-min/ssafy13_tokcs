# question/services/question_creation_service.py

from django.core.exceptions import PermissionDenied, ValidationError
from question.models.chapter import Chapter
from question.models.question import ObjectiveQuestion, SubjectiveQuestion, Choice
from django.contrib.auth import get_user_model

User = get_user_model()

def create_objective_question(user, data):
    """
    객관식 문제와 관련 보기를 생성하는 함수
    data 예시:
    {
      "chapter_id": 3,
      "content": "OSI 7계층 중 전송 계층의 역할은 무엇입니까?",
      "explanation": "데이터 전송이 핵심 역할입니다.",
      "score": 10,
      "question_type": "MCQ",   # 반드시 "MCQ"로 입력
      "choices": [
            {"content": "데이터 전송", "is_correct": True},
            {"content": "회선설정", "is_correct": False},
            {"content": "라우팅", "is_correct": False},
            {"content": "네트워크 관리", "is_correct": False}
      ]
    }
    """
    if not user.is_staff:
        raise PermissionDenied("문제 출제 권한이 없습니다.")

    try:
        chapter = Chapter.objects.get(id=data['chapter_id'])
    except Chapter.DoesNotExist:
        raise ValidationError("유효한 Chapter가 아닙니다.")

    # 객관식 문제 생성 (BaseQuestion의 필드 활용)
    question = ObjectiveQuestion.objects.create(
        chapter=chapter,
        question_type="MCQ",   # 객관식이므로 고정
        content=data['content'],
        explanation=data.get('explanation', ""),
        score=data.get('score', 5)  # 기본 배점이 없으면 5점
    )

    # 선택지(Choice) 생성
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
    """
    주관식 문제를 생성하는 함수
    data 예시:
    {
      "chapter_id": 3,
      "content": "네트워크 구성 요소를 나열하세요.",
      "explanation": "주관식 해설 예시",
      "score": 10,
      "question_type": "SA",   # 반드시 "SA"로 입력
      "keyword_ids": [1, 2, 5]  # 이미 생성된 Keyword들의 ID 리스트
    }
    """
    if not user.is_staff:
        raise PermissionDenied("문제 출제 권한이 없습니다.")

    try:
        chapter = Chapter.objects.get(id=data['chapter_id'])
    except Chapter.DoesNotExist:
        raise ValidationError("유효한 Chapter가 아닙니다.")

    question = SubjectiveQuestion.objects.create(
        chapter=chapter,
        question_type="SA",    # 주관식 문제
        content=data['content'],
        explanation=data.get('explanation', ""),
        score=data.get('score', 5)
    )

    # ManyToMany를 이용하여 키워드 연결 (중간 테이블을 통해서 연결됨)
    keyword_ids = data.get('keyword_ids', [])
    if keyword_ids:
        question.keywords.set(keyword_ids)
    return question

def create_multiple_questions(user, questions_data):
    """
    한 번에 여러 문제를 생성하는 함수.
    questions_data는 문제 정보를 담은 dict의 리스트입니다.
    각 dict는 반드시 "question_type" 필드를 포함해야 합니다.
      - "MCQ"일 경우, 객관식 문제 생성 로직을 사용.
      - "SA"일 경우, 주관식 문제 생성 로직을 사용.
    문제 출제 시, 권한 검사를 하여 권한이 없는 사용자는 출제할 수 없도록 합니다.
    
    만약 문제 하나라도 생성에 실패하면, 그에 대한 에러 메시지를 모아서 ValidationError를 발생시킬 수 있습니다.
    """
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
