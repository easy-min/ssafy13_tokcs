
import re

def normalize(text: str) -> str:
    """
    텍스트를 정규화하는 함수.
    - 모든 공백 제거
    - 소문자 변환
    """
    return re.sub(r'\s+', '', text).lower()

def grade_answer(answer_text: str, question) -> tuple[int, list[str]]:
    """
    주관식 문제 채점을 위한 함수.
    - answer_text: 사용자가 제출한 텍스트 답안
    - question: 채점 대상인 SubjectiveQuestion 인스턴스
     
    채점 로직:
    1. 사용자의 텍스트를 정규화한다.
    2. 문제와 연결된 모든 키워드 매핑(QuestionKeywordMapping)을 불러온다.
    3. 각 키워드에 대해, 키워드의 기본 단어와 동의어를 모두 정규화하여
       answer_text 내에 존재하는지 확인한다.
    4. 존재하면, 해당 키워드의 중요도(가중치)를 더하고, 매칭된 키워드를 리스트에 추가한다.
    5. 최종 점수와 매칭된 키워드 리스트를 반환한다.
    """
    # 해당 문제에 대해 연관된 모든 키워드 매핑
    from question.models.question import QuestionKeywordMapping

    norm_answer = normalize(answer_text)
    score = 0
    matched_keywords = []

    # 문제의 키워드 매핑을 불러옴 (select_related를 통해 불필요한 DB Hit 최소화)
    mappings = QuestionKeywordMapping.objects.filter(question=question).select_related('keyword')

    for mapping in mappings:
        keyword = mapping.keyword
        # 키워드의 기본 단어 및 동의어들을 정규화하여 모으기
        variants = [normalize(variant) for variant in keyword.all_variants()]
        for variant in variants:
            if variant in norm_answer:
                score += mapping.importance  # 중요도 만큼 점수 가중치 반영
                matched_keywords.append(keyword.word)  # 키워드의 원래 단어를 기록
                break  # 한 키워드 그룹에서 매칭되면 다음 매핑으로 넘어감
    return score, matched_keywords
