from django import forms
from exam.models import ParticipantProfile
from django.contrib.auth.models import User

class ParticipantExcelUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'}),
        help_text="Upload file Excel dengan 2 sheet: Sheet1 (Hari 1) dan Sheet2 (Hari 2)"
    )

class ParticipantManualForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = ParticipantProfile
        fields = ['full_name', 'school', 'day']
