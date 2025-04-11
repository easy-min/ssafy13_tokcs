# question/forms/subjective_question_forms.py

from django import forms
from question.models.question import SubjectiveQuestion
from question.models.chapter import Chapter
from question.models.question import Keyword

class SubjectiveQuestionForm(forms.ModelForm):
    class Meta:
        model = SubjectiveQuestion
        fields = ['chapter', 'content', 'explanation', 'score', 'keywords']
        labels = {
            'chapter': '단원 선택',
            'content': '문제 내용',
            'explanation': '해설',
            'score': '배점',
            'keywords': '정답 키워드 선택'
        }
        widgets = {
            'chapter': forms.Select(),
            'content': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 3}),
            'keywords': forms.CheckboxSelectMultiple(),
        }
    
    def clean_keywords(self):
        keywords = self.cleaned_data.get('keywords')
        if not keywords or len(keywords) == 0:
            raise forms.ValidationError("최소 하나 이상의 키워드를 선택해야 합니다.")
        return keywords
