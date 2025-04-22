# question/forms/problemset_forms.py
from django import forms
from question.models.problemSet import ProblemSet

class ProblemSetCreationForm(forms.ModelForm):
    class Meta:
        model = ProblemSet
        fields = ['title', 'description', 'scheduled_date', 'close_date', 'total_score']
        labels = {
            'title': '문제 세트 제목',
            'description': '설명',
            'scheduled_date': '시작 날짜',
            'close_date': '마감 날짜',
            'total_score': '총점'
        }
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'close_date': forms.DateInput(attrs={'type': 'date'})
        }
