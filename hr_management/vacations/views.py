from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count


from employees.models import Employee
from .models import VacationRequest, CompensatoryDay
from .forms import VacationRequestForm, CompensatoryDayForm

def is_hr(user):
    return user.is_staff

@login_required
def vacation_request_create(request):
    if request.method == 'POST':
        form = VacationRequestForm(request.POST)
        if form.is_valid():
            vacation_request = form.save()
            messages.success(request, 'Vacation request submitted.')
            # (Optional) Trigger an email notification here.
            return redirect('vacation_list')
    else:
        form = VacationRequestForm()
    return render(request, 'vacations/vacation_request.html', {'form': form})

@login_required
def vacation_list(request):
    # HR users see all requests; regular employees see only their own.
    if request.user.is_staff:
        vacations = VacationRequest.objects.all()
    else:
        vacations = VacationRequest.objects.filter(employee__user=request.user)
    return render(request, 'vacations/vacation_list.html', {'vacations': vacations})

@login_required
@user_passes_test(is_hr)
def vacation_approve(request, pk):
    vacation = get_object_or_404(VacationRequest, pk=pk)
    vacation.status = 'A'
    vacation.approved_by = request.user.username
    vacation.save()
    messages.success(request, 'Vacation approved.')
    # (Optional) Trigger an email notification here.
    return redirect('vacation_list')

@login_required
@user_passes_test(is_hr)
def vacation_reject(request, pk):
    vacation = get_object_or_404(VacationRequest, pk=pk)
    vacation.status = 'R'
    vacation.approved_by = request.user.username
    vacation.save()
    messages.success(request, 'Vacation rejected.')
    # (Optional) Trigger an email notification here.
    return redirect('vacation_list')

@login_required
def vacation_manage_view(request):
    """
    Displays employees with their vacation status and compensation details.
    """
    employees = Employee.objects.all()
    context = {
        'employees': employees,
        'now': timezone.now().date(),
    }
    return render(request, 'vacations/vacation_manage.html', context)

@login_required
@user_passes_test(is_hr)
def grant_vacation(request, employee_id):
    """
    Grants vacation for an eligible employee by creating an approved vacation request.
    But if the employee has pending compensatory days, those must be applied first.
    """
    employee = get_object_or_404(Employee, pk=employee_id)
    comp_days = employee.compensatory_days_available()
    if comp_days > 0:
        messages.error(request, f'Employee has {comp_days} compensatory day(s) available. Please apply these days before taking vacation.')
        return redirect('vacation_manage')
    
    if not employee.is_eligible_for_vacation():
        messages.error(request, 'Employee does not have enough vacation balance.')
        return redirect('vacation_manage')
    
    vacation_request = VacationRequest.objects.create(
        employee=employee,
        start_date=timezone.now().date(),
        duration=10,  # fixed duration, adjust as needed
        status='A',   # automatically approved in this example
        approved_by=request.user.username if request.user.is_authenticated else 'System'
    )
    messages.success(request, f'Vacation granted for {employee.name}.')
    return redirect('vacation_manage')

@login_required
@user_passes_test(is_hr)
def apply_deduction(request, pk):
    """
    Marks the vacation request as having its deduction applied.
    """
    vacation = get_object_or_404(VacationRequest, pk=pk)
    if vacation.return_date <= timezone.now().date() and not vacation.deduction_done:
        vacation.deduction_done = True
        vacation.save()
        messages.success(request, f'Deduction applied for {vacation.employee.name}\'s vacation request.')
    else:
        messages.error(request, 'Cannot apply deduction for this request.')
    return redirect('vacation_manage')

@login_required
@user_passes_test(is_hr)
def create_compensatory_days(request):
    """
    Allows HR to select multiple dates for compensatory days for an employee.
    """
    employees = Employee.objects.all()
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        dates_str = request.POST.get('dates')  # Expecting comma-separated dates (e.g., "2025-04-01,2025-04-03")
        note = request.POST.get('note', '')
        employee = get_object_or_404(Employee, pk=employee_id)
        
        if dates_str:
            dates = dates_str.split(',')
            for date_str in dates:
                date_str = date_str.strip()
                if date_str:
                    date = parse_date(date_str)
                    if date:
                        CompensatoryDay.objects.create(employee=employee, date=date, note=note)
            messages.success(request, "Compensatory days created successfully.")
        else:
            messages.error(request, "Please select at least one date.")
            
        return redirect('vacation_manage')
    
    return render(request, 'vacations/create_compensatory_days.html', {'employees': employees})

@login_required
@user_passes_test(is_hr)
def apply_compensation(request, employee_id):
    """
    Allows HR to mark all pending compensatory days for the employee as used.
    (Alternatively, you can let HR choose specific days.)
    """
    employee = get_object_or_404(Employee, pk=employee_id)
    pending = employee.compensatory_days_available()
    if pending > 0:
        # Mark all pending compensatory days as used with today's date.
        from .models import CompensatoryDay
        CompensatoryDay.objects.filter(employee=employee, used=False).update(used=True, used_date=timezone.now().date())
        messages.success(request, f'Applied {pending} compensatory day(s) for {employee.name}.')
    else:
        messages.error(request, 'No compensatory days available to apply.')
    return redirect('vacation_manage')

@login_required
@user_passes_test(is_hr)
def compensation_panel(request):
    """
    Displays a panel with all pending (unused) compensatory days.
    HR can review and apply these compensatory days.
    """
    # Import CompensatoryDay from models if not already imported
    comp_days = CompensatoryDay.objects.filter(used=False).order_by('date')
    context = {
        'comp_days': comp_days,
        'now': timezone.now().date(),
    }
    return render(request, 'vacations/compensation_panel.html', context)

def apply_compensation(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    pending = CompensatoryDay.objects.filter(employee=employee, used=False).count()
    if pending > 0:
        CompensatoryDay.objects.filter(employee=employee, used=False).update(used=True, used_date=timezone.now().date())
        messages.success(request, f'Applied {pending} compensatory day(s) for {employee.name}.')
    else:
        messages.error(request, 'No compensatory days available to apply.')
    return redirect('vacation_manage')

@login_required
@user_passes_test(is_hr)
def compensation_taken_list(request):
    """
    Displays a list of employees who have taken their compensatory days,
    along with the total number of days taken.
    """
    # Group used compensatory days by employee and count them.
    used_comp_days = (
        CompensatoryDay.objects.filter(used=True)
        .values('employee__id', 'employee__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    context = {
        'used_comp_days': used_comp_days,
    }
    return render(request, 'vacations/compensation_taken_list.html', context)