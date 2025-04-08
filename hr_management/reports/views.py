from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from employees.models import Employee
from django.utils import timezone
from xhtml2pdf import pisa
import openpyxl
from django.shortcuts import render


def reports_index(request):
    return render(request, 'reports/report.html')

def generate_pdf(request):
    today = timezone.now().date()
    employees = Employee.objects.all()

    # Monte uma lista de registros com as informações necessárias
    report_data = []
    for emp in employees:
        # Verifica se o funcionário está de férias
        # (Considera um pedido de férias com status "Approved" cujo período inclui a data de hoje)
        is_on_vacation = emp.vacationrequest_set.filter(
            status='A',
            start_date__lte=today,
            return_date__gte=today
        ).exists()
        
        # Conta quantos dias compensatórios foram utilizados
        from vacations.models import CompensatoryDay  # Evite import circular se necessário
        comp_days_taken = CompensatoryDay.objects.filter(employee=emp, used=True).count()
        
        report_data.append({
            'name': emp.name,
            'contract_date': emp.contract_date,
            'position': emp.position,
            'department': emp.department,
            'accumulated_vacation_days': emp.accumulated_vacation_days(),
            'is_on_vacation': is_on_vacation,
            'comp_days_taken': comp_days_taken,
        })

    # Renderiza o template usando report_data
    html = render_to_string('reports/report.html', {'employees': report_data})
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

def generate_excel(request):
    today = timezone.now().date()
    employees = Employee.objects.all()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Employees"

    # Cabeçalho do relatório com as novas colunas
    sheet.append([
        'Name',
        'Contract Date',
        'Position',
        'Department',
        'Accumulated Vacation Days',
        'On Vacation',
        'Compensatory Days Taken'
    ])

    from vacations.models import CompensatoryDay
    for emp in employees:
        is_on_vacation = emp.vacationrequest_set.filter(
            status='A',
            start_date__lte=today,
            return_date__gte=today
        ).exists()
        comp_days_taken = CompensatoryDay.objects.filter(employee=emp, used=True).count()
        sheet.append([
            emp.name,
            emp.contract_date,
            emp.position,
            emp.department,
            emp.accumulated_vacation_days(),
            "Yes" if is_on_vacation else "No",
            comp_days_taken,
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="employees.xlsx"'
    workbook.save(response)
    return response