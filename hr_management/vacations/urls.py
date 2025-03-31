from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.vacation_request_create, name='vacation_request'),
    path('', views.vacation_list, name='vacation_list'),
    path('approve/<int:pk>/', views.vacation_approve, name='vacation_approve'),
    path('reject/<int:pk>/', views.vacation_reject, name='vacation_reject'),
    path('manage/', views.vacation_manage_view, name='vacation_manage'),
    path('apply_deduction/<int:pk>/', views.apply_deduction, name='apply_deduction'),
    path('compensation/apply/<int:employee_id>/', views.apply_compensation, name='apply_compensation'),
    path('grant/<int:employee_id>/', views.grant_vacation, name='grant_vacation'),
    path('compensation/new/', views.create_compensatory_days, name='create_compensatory_days'),
    path('compensation/', views.compensation_panel, name='compensation_panel'),
    path('compensation/taken/', views.compensation_taken_list, name='compensation_taken_list'),
]
