from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'contract_date', 'position', 'department']

class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
