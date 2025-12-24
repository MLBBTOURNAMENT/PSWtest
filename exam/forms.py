from django import forms
from .models import Tryout, Question
from django.forms import inlineformset_factory

class TryoutForm(forms.ModelForm):
    publish_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    class Meta:
        model = Tryout
        fields = ['title', 'description', 'subjects', 'publish_time', 'work_time_minutes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'subjects': forms.TextInput(attrs={'placeholder': 'Matematika · Fisika · Kimia'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['number', 'text', 'option_a', 'option_b',
                  'option_c', 'option_d', 'correct_option', 'score']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

QuestionFormSet = inlineformset_factory(
    Tryout,
    Question,
    form=QuestionForm,
    extra=1,          # minimal 1 form kosong
    can_delete=True   # bisa hapus soal
)
