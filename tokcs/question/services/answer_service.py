import re
from django.core.exceptions import ObjectDoesNotExist
from tokcs.question.models.question import (
    ObjectiveQuestion, SubjectiveQuestion, Choice, 
    QuestionKeywordMapping
)
from tokcs.question.models.choice import ObjectiveAnswer, SubjectiveAnswer

# --- 유틸리티 함수: 텍스트 정규화
def normalize(text: str) -> str:
    """
    텍스트에서 공백을 제거하고 소문자로 변환.
    주관식 채점 시 문자열 비교의 일관성을 위해 사용.
    """
    return re.sub(r'\s+', '', text).lower()

# --- 주관식 문제 채점 함수 (grade_answer)
def grade_answer(answer_text: str, question: SubjectiveQuestion) -> tuple[int, list[str]]:
    """
    주관식 문제에 대해 텍스트 답안을 채점하는 함수.
    """
    norm_answer = normalize(answer_text)
    score = 0
    matched_keywords = []
    
    mappings = QuestionKeywordMapping.objects.filter(question=question).select_related('keyword')
    for mapping in mappings:
        keyword = mapping.keyword
        # 키워드의 기본 단어와 동의어 목록을 함께 비교
        variants = [normalize(variant) for variant in keyword.all_variants()]
        for variant in variants:
            if variant in norm_answer:
                score += mapping.importance  # 중요도 가중치를 더함
                matched_keywords.append(keyword.word)  # 원래 단어 기록
                break   # 해당 키워드 그룹은 한 번만 매칭
    return score, matched_keywords

# --- 객관식 문제 채점 함수
def grade_objective_answer(objective_answer: ObjectiveAnswer) -> int:
    """
    객관식 문제 답안을 채점하는 함수.
    """
    try:
        selected_choice = objective_answer.selected_choice
    except ObjectDoesNotExist:
        objective_answer.score = 0
        objective_answer.save()
        return 0

    if selected_choice.is_correct:
        objective_answer.score = objective_answer.question.score
    else:
        objective_answer.score = 0
    
    objective_answer.save()
    return objective_answer.score

# --- 주관식 문제 정답 채점 서비스
def grade_subjective_answer(subjective_answer: SubjectiveAnswer) -> tuple[int, list[str]]:
    """
    주관식 문제 답안을 채점합니다.
    """
    score, matched_keywords = grade_answer(subjective_answer.answer_text, subjective_answer.question)
    subjective_answer.score = score
    subjective_answer.matched_keywords = matched_keywords
    subjective_answer.save()
    return score, matched_keywords
