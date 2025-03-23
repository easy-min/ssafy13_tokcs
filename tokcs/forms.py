# tokcs/forms.py
from django import forms
from .models import QuizQuestion

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['chapter', 'question_text', 'answer_text', 'keywords', 'explanation', 'is_tail_question']
        widgets = {
            'question_text': forms.Textarea(attrs={'placeholder': '질문 내용을 입력하세요', 'rows': 4}),
            'answer_text': forms.Textarea(attrs={'placeholder': '모범 답안을 입력하세요', 'rows': 4}),
            'explanation': forms.Textarea(attrs={'placeholder': '해설을 입력하세요', 'rows': 3}),
        }

