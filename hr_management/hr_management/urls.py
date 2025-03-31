from django.contrib import admin
from django.urls import path, include
from .views import home  # Certifique-se de ter definido essa view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Home page
    path('employees/', include('employees.urls')),
    path('vacations/', include('vacations.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('reports/', include('reports.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
