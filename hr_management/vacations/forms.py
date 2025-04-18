from django import forms
from employees.models import Employee
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

class VacationRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = VacationRequest
        # Supondo que queremos atualizar a data de início e a duração
        fields = ['start_date', 'duration']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'duration': forms.NumberInput(attrs={'min': 1}),
        }       

class CompensatoryDayBulkForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label="Funcionário"
    )
    dates = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'datepicker',
            'placeholder': 'Clique e selecione as datas...'
        }),
        help_text="Selecione uma ou mais datas"
    )
    note = forms.CharField(
        widget=forms.Textarea(attrs={'rows':3}),
        required=False
    )