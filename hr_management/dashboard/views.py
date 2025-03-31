from django.shortcuts import render
from employees.models import Employee
from vacations.models import VacationRequest, CompensatoryDay
from datetime import timedelta
from django.utils import timezone

def dashboard_view(request):
    total_employees = Employee.objects.count()
    vacation_requests = VacationRequest.objects.all()
    pending_requests = vacation_requests.filter(status='P').count()
    approved_requests = vacation_requests.filter(status='A').count()
    
    # Sample metric: % eligible (e.g., employees with contract >6 months)
    eligible_count = Employee.objects.filter(
        contract_date__lte=timezone.now().date() - timedelta(days=180)
    ).count()
    percent_eligible = (eligible_count / total_employees * 100) if total_employees > 0 else 0

    # Prepare data for charts
    chart_data = {
        'vacation_status': {
            'labels': ['Pending', 'Approved', 'Rejected'],
            'data': [
                vacation_requests.filter(status='P').count(),
                vacation_requests.filter(status='A').count(),
                vacation_requests.filter(status='R').count()
            ]
        },
        'compensatory': {
            'labels': ['Used', 'Pending'],
            'data': [
                CompensatoryDay.objects.filter(used=True).count(),
                CompensatoryDay.objects.filter(used=False).count()
            ]
        }
    }

    context = {
        'total_employees': total_employees,
        'percent_eligible': percent_eligible,
        'chart_data': chart_data,
    }
    return render(request, 'dashboard/dashboard.html', context)
