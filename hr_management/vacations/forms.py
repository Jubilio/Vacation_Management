from django import forms
from .models import VacationRequest, CompensatoryDay

class VacationRequestForm(forms.ModelForm):
    class Meta:
        model = VacationRequest
        fields = ['employee', 'start_date', 'duration']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CompensatoryDayForm(forms.ModelForm):
    class Meta:
        model = CompensatoryDay
        fields = ['employee', 'date', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Justification (if needed)'}),
        }
