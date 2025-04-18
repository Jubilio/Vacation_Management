from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from employees.models import Employee
from vacations.models import VacationRequest, CompensatoryDay
import json

@login_required
def dashboard_view(request):
    # Data de hoje
    today = timezone.now().date()

    # KPIs
    total_employees = Employee.objects.count()
    vacations_running = VacationRequest.objects.filter(
        status='A', start_date__lte=today, return_date__gte=today
    ).count()
    pending_requests = VacationRequest.objects.filter(status='P').count()

    # Métrica: % de elegíveis (contrato > 6 meses)
    eligible_count = Employee.objects.filter(
        contract_date__lte=today - timezone.timedelta(days=180)
    ).count()
    percent_eligible = (eligible_count / total_employees * 100) if total_employees else 0

    # Compensatory metrics
    comp_used = CompensatoryDay.objects.filter(used=True).count()
    comp_pending = CompensatoryDay.objects.filter(used=False).count()

    # Dados para gráficos
    status_counts = list(
        VacationRequest.objects.values('status').annotate(total=Count('id'))
    )
    labels_vac = [item['status'] for item in status_counts]
    data_vac = [item['total'] for item in status_counts]

    comp_labels = ['Usados', 'Pendentes']
    comp_data = [comp_used, comp_pending]

    context = {
        'total_employees': total_employees,
        'vacations_running': vacations_running,
        'pending_requests': pending_requests,
        'percent_eligible': percent_eligible,
        'comp_used': comp_used,
        'comp_pending': comp_pending,
        'vac_labels_json': json.dumps(labels_vac),
        'vac_data_json': json.dumps(data_vac),
        'comp_labels_json': json.dumps(comp_labels),
        'comp_data_json': json.dumps(comp_data),
    }
    return render(request, 'dashboard/dashboard.html', context)