from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import User , Questions, Answer,Marks,QTAnswer
from django.forms.utils import ValidationError

role_choice = (
    ("QuizTaker","QuizTaker"),
    ("QuizMaster", "QuizMaster"), 
)

class UserRegisterForms(UserCreationForm):
    username = forms.CharField(max_length=15)
    role_choice = forms.ChoiceField(choices=role_choice)
   
    class Meta :
        model = User
        fields = ['username' , 'password1' , 'password2','role_choice']

    def save(self, commit=True):
        user = super(UserRegisterForms, self).save(commit=False)
        if commit:
            user.save()
        return user
    
class TakeQuizForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = QTAnswer
        fields = ('answer', )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question') 
        super(TakeQuizForm, self).__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answer.order_by('Answer_content')

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Questions
        fields = ('question_content', )

class QuestionTypeForm(forms.ModelForm):
    class Meta:
        model = Questions
        fields = ('question_type',)

class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ('positive_marking', 'negative_marking', )

class AnswerForm(forms.ModelForm):
    """Form definition for Answer"""

    class Meta:
        """Meta definition for Answerform."""

        model = Answer
        fields = ('Answer_content', 'is_correct' , )

class NumericalAnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('numerical_option',)

class BooleanAnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('boolean_question',)


class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        has_one_correct_answer = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_one_correct_answer = True
                    break
        if not has_one_correct_answer:
            raise ValidationError('Mark at least one answer as correct.', code='no_correct_answer')