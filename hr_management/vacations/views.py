from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q

from employees.models import Employee
from .models import VacationRequest, CompensatoryDay
from .forms import (
    VacationRequestForm,
    VacationRequestUpdateForm,
    CompensatoryDayForm,
    CompensatoryDayBulkForm,
)
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
    Exibe os funcionários com suas informações de férias e compensação.
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
    Concede férias para um funcionário elegível, mas se houver dias compensatórios pendentes,
    solicita que estes sejam aplicados antes.
    """
    employee = get_object_or_404(Employee, pk=employee_id)
    # Utiliza a propriedade compensatory_days_available (definida no model Employee)
    comp_days = employee.compensatory_days_available
    if comp_days > 0:
        messages.error(
            request,
            f'O funcionário possui {comp_days} dia(s) compensatório(s) pendentes. Por favor, aplique esses dias antes de conceder novas férias.'
        )
        return redirect('vacation_manage')
    
    if not employee.is_eligible_for_vacation():
        messages.error(request, 'O funcionário não possui saldo suficiente de férias.')
        return redirect('vacation_manage')
    
    vacation_request = VacationRequest.objects.create(
        employee=employee,
        start_date=timezone.now().date(),
        duration=10,  # duração fixa; ajuste conforme necessário
        status='A',   # aprovado automaticamente para este exemplo
        approved_by=request.user.username if request.user.is_authenticated else 'System'
    )
    messages.success(request, f'Férias concedidas para {employee.name}.')
    return redirect('vacation_manage')

@login_required
@user_passes_test(is_hr)
def apply_deduction(request, pk):
    """
    Marca o pedido de férias como tendo tido o desconto aplicado após o retorno.
    """
    vacation = get_object_or_404(VacationRequest, pk=pk)
    if vacation.return_date <= timezone.now().date() and not vacation.deduction_done:
        vacation.deduction_done = True
        vacation.save()
        messages.success(
            request,
            f'Desconto aplicado para o pedido de férias de {vacation.employee.name}.'
        )
    else:
        messages.error(request, 'Não é possível aplicar o desconto para este pedido.')
    return redirect('vacation_manage')

@login_required
@user_passes_test(is_hr)
def create_compensatory_days(request):
    """
    Formulário único pra escolher o funcionário, várias datas e nota.
    """
    if request.method == 'POST':
        form = CompensatoryDayBulkForm(request.POST)
        if form.is_valid():
            emp    = form.cleaned_data['employee']
            dates  = form.cleaned_data['dates'].split(',')
            note   = form.cleaned_data['note']
            for d in dates:
                d = d.strip()
                if d:
                    dt = parse_date(d)
                    if dt:
                        CompensatoryDay.objects.create(
                            employee=emp,
                            date=dt,
                            note=note
                        )
            messages.success(request, "Dias compensatórios registrados com sucesso.")
            return redirect('vacation_manage')
    else:
        form = CompensatoryDayBulkForm()

    return render(request, 'vacations/create_compensatory_days.html', {
        'form': form
    })

@login_required
@user_passes_test(is_hr)
def apply_compensation(request, employee_id):
    """
    Permite que o RH aplique (marque como usados) todos os dias compensatórios pendentes de um funcionário.
    """
    employee = get_object_or_404(Employee, pk=employee_id)
    pending = CompensatoryDay.objects.filter(employee=employee, used=False).count()
    if pending > 0:
        CompensatoryDay.objects.filter(employee=employee, used=False).update(
            used=True, used_date=timezone.now().date()
        )
        messages.success(request, f'Aplicados {pending} dia(s) compensatório(s) para {employee.name}.')
    else:
        messages.error(request, 'Nenhum dia compensatório disponível para aplicar.')
    return redirect('vacation_manage')

@login_required
@user_passes_test(is_hr)
def compensation_panel(request):
    """
    Displays a panel with all employees who have pending compensatory days.
    Allows HR to apply a specific number of compensatory days per employee.
    """
    # Handle form submission to apply days
    if request.method == 'POST':
        emp_id = request.POST.get('employee_id')
        days_to_apply = int(request.POST.get('apply_days', 0))
        employee = get_object_or_404(Employee, pk=emp_id)
        # Count pending days
        pending_qs = CompensatoryDay.objects.filter(employee=employee, used=False).order_by('date')
        total_pending = pending_qs.count()
        if days_to_apply <= 0 or days_to_apply > total_pending:
            messages.error(request, f"Invalid number of days. Employee has {total_pending} pending.")
        else:
            # Mark the oldest 'days_to_apply' as used
            to_apply = pending_qs[:days_to_apply]
            for cd in to_apply:
                cd.used = True
                cd.used_date = timezone.now().date()
                cd.save()
            messages.success(request, f"Applied {days_to_apply} compensatory day(s) for {employee.name}.")
        return redirect('compensation_panel')

    # GET: build list of employees with pending counts
    employees = Employee.objects.annotate(
        pending_days=Count('compensatoryday', filter=Q(compensatoryday__used=False))
    ).filter(pending_days__gt=0)
    context = {
        'employees': employees,
    }
    return render(request, 'vacations/compensation_panel.html', context)

@login_required
@user_passes_test(is_hr)
def compensation_taken_list(request):
    """
    Exibe uma lista de funcionários que já utilizaram seus dias compensatórios,
    juntamente com o total de dias utilizados.
    """
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

@login_required
@user_passes_test(is_hr)
def update_vacation_request(request, pk):
    """
    Permite atualizar os dados de um pedido de férias após sua concessão,
    para modificar a data de início ou a duração, caso seja necessário.
    """
    vacation = get_object_or_404(VacationRequest, pk=pk)
    
    # Se a data de retorno deve ser recalculada automaticamente com base na duração,
    # ela será recalculada quando salvarmos o objeto (a lógica já presente em save()).
    
    if request.method == 'POST':
        form = VacationRequestUpdateForm(request.POST, instance=vacation)
        if form.is_valid():
            form.save()
            messages.success(request, "Detalhes das férias atualizados com sucesso.")
            return redirect('vacation_manage')
    else:
        form = VacationRequestUpdateForm(instance=vacation)
    
    return render(request, 'vacations/update_vacation_request.html', {'form': form, 'vacation': vacation})

@login_required
@user_passes_test(is_hr)
def create_compensatory_days(request):
    if request.method == 'POST':
        form = CompensatoryDayBulkForm(request.POST)
        if form.is_valid():
            emp    = form.cleaned_data['employee']
            dates  = form.cleaned_data['dates'].split(',')    # vem “2025-04-01,2025-04-03,…”
            note   = form.cleaned_data['note']
            for d in dates:
                d = d.strip()
                if d:
                    dt = parse_date(d)
                    if dt:
                        CompensatoryDay.objects.create(
                            employee=emp,
                            date=dt,
                            note=note
                        )
            messages.success(request, "Dias compensatórios registrados com sucesso.")
            return redirect('vacation_manage')
    else:
        form = CompensatoryDayBulkForm()
    return render(request, 'vacations/create_compensatory_days.html', {'form': form})