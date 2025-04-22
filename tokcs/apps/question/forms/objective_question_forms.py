from django import forms
from django.forms.models import inlineformset_factory
from question.models.question import ObjectiveQuestion, Choice

class ObjectiveQuestionForm(forms.ModelForm):
    class Meta:
        model = ObjectiveQuestion
        # creator, created_at 은 뷰에서 할당하므로 폼에서는 제외
        exclude = ['creator', 'created_at', 'question_type']
        widgets = {
            'chapter': forms.Select(),
            'content': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 3}),
        }

# Choice용 inline formset (ObjectiveQuestion ↔ Choice : 1:N)
ChoiceFormSet = inlineformset_factory(
    ObjectiveQuestion,
    Choice,
    fields      = ['content', 'is_correct'],
    extra       = 4,               # 기본으로 4개 보기 생성
    can_delete  = True,            # 삭제 체크박스 제공
    widgets     = {
        'content': forms.TextInput(attrs={'placeholder': '보기 내용을 입력하세요'}),
        'is_correct': forms.CheckboxInput(),
    }
)
