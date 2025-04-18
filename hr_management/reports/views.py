from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse              # <— para enviar o arquivo Excel
from django.template.loader import render_to_string
from django.db.models import Q, Sum, Count
from django.utils import timezone
import openpyxl                                   # <— não esqueça!
from employees.models import Employee
from vacations.models import VacationRequest, CompensatoryDay
from xhtml2pdf import pisa

@login_required
def reports_index(request):
    # … your existing code …
    return render(request, 'reports/index.html', context)

@login_required
def generate_pdf(request):
    # pull filters
    name       = request.GET.get('name', '')
    department = request.GET.get('department', '')
    qs         = Employee.objects.all()
    if name:       qs = qs.filter(name__icontains=name)
    if department: qs = qs.filter(department__icontains=department)

    # build enriched report_data
    today       = timezone.now().date()
    report_data = []
    for emp in qs:
        taken = emp.vacationrequest_set.filter(
            status='A', return_date__lte=today
        ).aggregate(total=Sum('duration'))['total'] or 0

        pending_vac = emp.accumulated_vacation_days() - taken
        comp_used   = CompensatoryDay.objects.filter(employee=emp, used=True).count()
        comp_pending= CompensatoryDay.objects.filter(employee=emp, used=False).count()

        report_data.append({
            'name'         : emp.name,
            'contract_date': emp.contract_date,
            'position'     : emp.position,
            'department'   : emp.department,
            'accumulated'  : emp.accumulated_vacation_days(),
            'vac_taken'    : taken,
            'vac_pending'  : pending_vac,
            'comp_used'    : comp_used,
            'comp_pending' : comp_pending,
        })

    context = {
        'name'      : name,
        'department': department,
        'employees' : report_data,
    }

    html = render_to_string('reports/report_pdf.html', context, request=request)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

@login_required
def generate_excel(request):
    # 1) filtros
    name = request.GET.get('name', '')
    department = request.GET.get('department', '')
    qs = Employee.objects.all()
    if name:
        qs = qs.filter(name__icontains=name)
    if department:
        qs = qs.filter(department__icontains=department)

    # 2) prepara o workbook
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Relatórios"

    # 3) cabeçalho
    sheet.append([
        'Nome',
        'Data de Contrato',
        'Cargo',
        'Departamento',
        'Férias Acumuladas',
        'Férias Tiradas',
        'Férias Pendentes',
        'Compensados Usados',
        'Compensados Pendentes',
    ])

    # 4) preenche linhas
    today = timezone.now().date()
    for emp in qs:
        vac_taken = (
            VacationRequest.objects
            .filter(employee=emp, status='A', return_date__lte=today)
            .aggregate(total=Sum('duration'))['total'] or 0
        )
        vac_pending = emp.accumulated_vacation_days() - vac_taken
        comp_used = CompensatoryDay.objects.filter(employee=emp, used=True).count()
        comp_pending = CompensatoryDay.objects.filter(employee=emp, used=False).count()

        sheet.append([
            emp.name,
            emp.contract_date,
            emp.position,
            emp.department,
            emp.accumulated_vacation_days(),
            vac_taken,
            vac_pending,
            comp_used,
            comp_pending,
        ])

    # 5) retorna o Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="relatorio_funcionarios.xlsx"'
    workbook.save(response)
    return response
