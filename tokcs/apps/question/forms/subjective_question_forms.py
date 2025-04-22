from django.forms import ModelForm, forms
from django.forms.models import inlineformset_factory
from tokcs.apps.question.models.question import SubjectiveQuestion, QuestionKeywordMapping

class SubjectiveQuestionForm(ModelForm):
    class Meta:
        model   = SubjectiveQuestion
        exclude = ['creator', 'created_at']
        # 모델에서 이미 labels 와 widgets 설정해둠

# QuestionKeywordMapping용 폼셋
# ManyToMany 연결에서 만약 단순 연결뿐만 아니라 다른 정보도 같이 담아야 하는 경우 thorugh 인수 사용해 중간 모델 매개자 역할
QuestionKeywordFormSet = inlineformset_factory(
    SubjectiveQuestion,
    QuestionKeywordMapping,
    fields      = ['keyword', 'importance'],
    extra       = 1,         # 기본 보일 매핑 행 개수
    can_delete  = True,
    widgets     = {
        'importance': forms.NumberInput(attrs={'min':1, 'max':10}),
    }
)
