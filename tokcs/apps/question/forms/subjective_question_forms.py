# question/forms/subjective_question_forms.py

from django import forms
from ..models.question import SubjectiveQuestion
from ..models.chapter import Chapter

class SubjectiveQuestionForm(forms.ModelForm):
    class Meta:
        model = SubjectiveQuestion
        # keywords 필드를 제외합니다.
        fields = ['chapter', 'content', 'explanation', 'score']
        labels = {
            'chapter': '단원 선택',
            'content': '문제 내용',
            'explanation': '해설',
            'score': '배점',
        }
        widgets = {
            'chapter': forms.Select(),
            'content': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 3}),
        }
