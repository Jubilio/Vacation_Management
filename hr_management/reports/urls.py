from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_index, name='reports_index'),
    path('pdf/', views.generate_pdf, name='report_pdf'),
    path('excel/', views.generate_excel, name='report_excel'),
]
