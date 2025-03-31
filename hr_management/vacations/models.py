from django.db import models
from datetime import timedelta
from employees.models import Employee

STATUS_CHOICES = [
    ('P', 'Pending'),
    ('A', 'Approved'),
    ('R', 'Rejected'),
]

class Holiday(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField(unique=True)

    def __str__(self):
        return f"{self.name} on {self.date}"

class VacationRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    duration = models.PositiveIntegerField(help_text="Duration in working days")
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    request_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.CharField(max_length=255, blank=True, null=True)
    deduction_done = models.BooleanField(default=False, help_text="Indicates if vacation discount has been applied after return.")

    def calculate_return_date(self):
        """
        Calculates the return date by skipping weekends and holidays.
        """
        current_date = self.start_date
        days_added = 0
        while days_added < self.duration:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5 and not Holiday.objects.filter(date=current_date).exists():
                days_added += 1
        return current_date

    def save(self, *args, **kwargs):
        if not self.return_date:
            self.return_date = self.calculate_return_date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Vacation Request for {self.employee.name} starting {self.start_date}"

class CompensatoryDay(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    used = models.BooleanField(default=False)
    used_date = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True, null=True, help_text="Justification note for this compensation (if any)")

    def __str__(self):
        return f"Compensatory Day for {self.employee.name} on {self.date}"

def compensatory_days_available(self):
    from vacations.models import CompensatoryDay
    return CompensatoryDay.objects.filter(employee=self, used=False).count()
