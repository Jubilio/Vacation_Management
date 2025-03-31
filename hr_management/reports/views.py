from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from employees.models import Employee
import openpyxl
from xhtml2pdf import pisa

from django.shortcuts import render

def reports_index(request):
    return render(request, 'reports/report.html')


def generate_pdf(request):
    employees = Employee.objects.all()
    html = render_to_string('reports/report.html', {'employees': employees})
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

def generate_excel(request):
    employees = Employee.objects.all()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Employees"
    sheet.append(['Name', 'Contract Date', 'Position', 'Department', 'Accumulated Vacation Days'])
    for emp in employees:
        sheet.append([
            emp.name,
            emp.contract_date,
            emp.position,
            emp.department,
            emp.accumulated_vacation_days()
        ])
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="employees.xlsx"'
    workbook.save(response)
    return response
