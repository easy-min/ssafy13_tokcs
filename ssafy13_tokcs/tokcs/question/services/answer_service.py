from django.core.exceptions import ObjectDoesNotExist
from question.models.questions import ObjectiveQuestion, SubjectiveQuestion, Choice
from question.models.answer import ObjectiveAnswer, SubjectiveAnswer
from question.services.grading_service import grade_answer

def grade_objective_answer(objective_answer):
    """
    객관식 답안을 채점
    1. 사용자가 제출한 ObjectiveAnswer의 selected_choice가 
       해당 문제(ObjectiveQuestion)의 정답인지 is_correct를 확인
    2. 정답이면 문제의 배점(question.score)을, 오답이면 0점을 부여
    3. 채점 결과를 해당 ObjectiveAnswer 객체에 저장하고, 점수를 반환
    """
    try:
        selected_choice = objective_answer.selected_choice
    except ObjectDoesNotExist:
        # 선택된 보기 정보가 없으면 0점으로 처리
        objective_answer.score = 0
        objective_answer.save()
        return 0

    # 채점 로직: 선택한 보기가 정답이면 문제의 배점을, 아니면 0점
    if selected_choice.is_correct:
        objective_answer.score = objective_answer.question.score
    else:
        objective_answer.score = 0

    objective_answer.save()
    return objective_answer.score

def grade_subjective_answer(subjective_answer):
    """
    주관식 답안을 채점
    1. 사용자가 입력한 텍스트(answer_text)와 해당 문제에 설정된 키워드(및 동의어)를 비교
    2. 채점 로직(grade_answer 함수)을 통해, 매칭된 키워드의 수와 중요도(가중치)에 따라 점수를 산출하고,
       매칭된 키워드 목록을 반환
    3. 이 결과들을 SubjectiveAnswer 객체에 저장하고, (score, matched_keywords)를 반환
    """
    score, matched_keywords = grade_answer(subjective_answer.answer_text, subjective_answer.question)
    subjective_answer.score = score
    subjective_answer.matched_keywords = matched_keywords
    subjective_answer.save()
    return subjective_answer.score, subjective_answer.matched_keywords
