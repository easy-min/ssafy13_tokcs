# services/answer_service.py

import re
from django.core.exceptions import ObjectDoesNotExist
from question.models.question import (
    ObjectiveQuestion, SubjectiveQuestion, Choice, 
    QuestionKeywordMapping
)
from question.models.choice import ObjectiveAnswer, SubjectiveAnswer

# --- 유틸리티 함수: 텍스트 정규화 (공백을 제거하고 소문자로 변환)
def normalize(text: str) -> str:
    return re.sub(r'\s+', '', text).lower()

# --- 주관식 문제 채점 함수 (grade_answer)
def grade_answer(answer_text: str, question: SubjectiveQuestion) -> tuple[int, list[str]]:
    """
    주관식 문제에 대해 텍스트 답안을 채점하는 함수.
    
    로직:
      1. 사용자의 answer_text를 normalize()를 통해 정규화.
      2. 해당 question에 연결된 QuestionKeywordMapping을 조회.
      3. 각 매핑에 대해, 연결된 키워드의 기본 단어와 동의어(all_variants())를 정규화한 후
         정규화된 answer_text 내 존재 여부를 확인.
      4. 존재하면 해당 매핑의 importance 만큼 점수를 추가하고, 
         매칭된 키워드(대표단어)를 매칭 리스트에 추가.
         
    반환:
      (최종 점수, 매칭된 키워드 리스트)
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
    
    로직:
      - 사용자가 제출한 ObjectiveAnswer에서 selected_choice (Choice)를 확인.
      - 해당 Choice의 is_correct가 True이면 문제의 배점(문제.score)을 반환, 아니면 0을 반환합니다.
      - 채점 결과는 ObjectiveAnswer 모델의 score 필드에 저장.
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
    
    로직:
      - 제출된 answer_text와 연결된 SubjectiveQuestion을 기반으로, grade_answer 함수를 호출.
      - 반환된 점수와 매칭된 키워드 목록을 SubjectiveAnswer 모델에 저장하고 반환.
    """
    score, matched_keywords = grade_answer(subjective_answer.answer_text, subjective_answer.question)
    subjective_answer.score = score
    subjective_answer.matched_keywords = matched_keywords
    subjective_answer.save()
    return score, matched_keywords
