from django.db import models
from django.utils import timezone
from datetime import timedelta

class Employee(models.Model):
    name = models.CharField(max_length=255)
    contract_date = models.DateField()
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True, null=True)
    # other fields as needed

    def __str__(self):
        return self.name

    def accumulated_vacation_days(self):
        """
        Accumulates 2 vacation days per month since contract_date.
        """
        now = timezone.now().date()
        months = (now.year - self.contract_date.year) * 12 + (now.month - self.contract_date.month)
        return months * 2

    def vacation_taken_days(self):
        """
        Sums up the duration of approved vacation requests whose return date has passed.
        """
        from vacations.models import VacationRequest
        approved_vacations = VacationRequest.objects.filter(
            employee=self,
            status='A',
            return_date__lte=timezone.now().date()
        )
        return sum(vac.duration for vac in approved_vacations)

    def vacation_balance(self):
        """
        Returns the difference between accumulated days and taken days.
        """
        return self.accumulated_vacation_days() - self.vacation_taken_days()

    def is_eligible_for_vacation(self):
        """
        Eligible if there is a positive vacation balance.
        """
        return self.vacation_balance() > 0

    def pending_compensatory_days(self):
        """
        Returns pending (unused) compensatory day records.
        """
        from vacations.models import CompensatoryDay
        return CompensatoryDay.objects.filter(employee=self, used=False)

class AuditLog(models.Model):
    user = models.CharField(max_length=255)
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action} on {self.model_name}"

