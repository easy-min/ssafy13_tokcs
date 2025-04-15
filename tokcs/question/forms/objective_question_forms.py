# question/forms/objective_question_forms.py

from django import forms
from question.models.question import ObjectiveQuestion, Choice
from question.models.chapter import Chapter

class ObjectiveQuestionForm(forms.ModelForm):
    # 객관식 선택지를 콤마로 구분하여 입력받는 추가 필드
    # 실제 운영시 Formset을 사용하면 더 좋습니다.
    choices_text = forms.CharField(
        label="객관식 보기 (콤마로 구분하여 입력)",
        help_text="예: 답안, 오답1, 오답2, 오답3",
        required=True
    )
    
    class Meta:
        model = ObjectiveQuestion
        fields = ['chapter', 'content', 'explanation', 'score']
        labels = {
            'chapter': '단원 선택',
            'content': '문제 내용',
            'explanation': '해설',
            'score': '배점'
        }
        widgets = {
            'chapter': forms.Select(),
            'content': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_choices_text(self):
        data = self.cleaned_data['choices_text']
        choices = [ct.strip() for ct in data.split(',') if ct.strip()]
        if not choices:
            raise forms.ValidationError("최소 하나 이상의 선택지를 입력해야 합니다.")
        return choices
