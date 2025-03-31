from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Employee
from .forms import EmployeeForm
import csv
import io
from .forms import CSVImportForm

def is_hr(user):
    return user.is_staff  # Only HR users are allowed

@login_required
@user_passes_test(is_hr)
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees})

@login_required
@user_passes_test(is_hr)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee created successfully.')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_create.html', {'form': form})

@login_required
@user_passes_test(is_hr)
def csv_import(request):
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)  # Skip header
            for row in csv.reader(io_string, delimiter=',', quotechar='"'):
                Employee.objects.create(
                    name=row[0],
                    contract_date=row[1],
                    position=row[2],
                    department=row[3] if len(row) > 3 else ''
                )
            messages.success(request, 'CSV data imported successfully.')
            return redirect('employee_list')
    else:
        form = CSVImportForm()
    return render(request, 'employees/csv_import.html', {'form': form})

@login_required
@user_passes_test(is_hr)
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully.')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_update.html', {'form': form, 'employee': employee})

@login_required
@user_passes_test(is_hr)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee removed successfully.')
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})
