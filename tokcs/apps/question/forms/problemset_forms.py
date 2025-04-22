from django import forms
from django.utils import timezone
from question.models.problemSet import ProblemSet
from question.models.chapter    import Chapter
from question.models.topic      import Topic

class ProblemSetForm(forms.ModelForm):
    # 추가 필드
    topic              = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        label="Topic 선택",
        required=True
    )
    chapters           = forms.ModelMultipleChoiceField(
        queryset=Chapter.objects.none(),  # init 에서 채워줄 예정
        label="Chapter 선택",
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    total_questions    = forms.IntegerField(label="총 문제 개수", min_value=1)
    objective_ratio    = forms.IntegerField(label="객관식 비율(%)", min_value=0, max_value=100)
    subjective_ratio   = forms.IntegerField(label="주관식 비율(%)", min_value=0, max_value=100)
    scheduled_date     = forms.DateField(label="시작 날짜", initial=timezone.now)
    close_date         = forms.DateField(label="마감 날짜", initial=timezone.now)
    pass_threshold     = forms.IntegerField(label="합격 기준(%)", min_value=0, max_value=100)

    class Meta:
        model  = ProblemSet
        fields = ['title', 'description', 'total_score', 'pass_threshold']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # topic 선택 시 자바스크립트로 chapter 필터링하지만,
        # 기본은 전체 chapter 목록을 보여줌
        self.fields['chapters'].queryset = Chapter.objects.all()

    def clean(self):
        cleaned = super().clean()
        obj = cleaned.get('objective_ratio', 0)
        sub = cleaned.get('subjective_ratio', 0)
        if obj + sub != 100:
            raise forms.ValidationError("객관식 비율 + 주관식 비율의 합은 100이어야 합니다.")
        if cleaned.get('close_date') <= cleaned.get('scheduled_date'):
            raise forms.ValidationError("마감 날짜는 시작 날짜 이후여야 합니다.")
        return cleaned
