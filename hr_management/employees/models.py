from django.db import models
from django.utils import timezone
from datetime import timedelta


class Employee(models.Model):
    name = models.CharField(max_length=255)
    contract_date = models.DateField()
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True, null=True)
    # Outros campos conforme necessário

    def __str__(self):
        return self.name

    def accumulated_vacation_days(self):
        """
        Acumula 2 dias de férias por mês a partir da data de contratação.
        """
        now = timezone.now().date()
        months = (now.year - self.contract_date.year) * 12 + (now.month - self.contract_date.month)
        return months * 2

    def vacation_taken_days(self):
        """
        Soma a duração dos pedidos de férias aprovados cujo dia de retorno já passou.
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
        Retorna a diferença entre os dias acumulados e os dias de férias já usufruídos.
        """
        return self.accumulated_vacation_days() - self.vacation_taken_days()

    def is_eligible_for_vacation(self):
        """
        Retorna True se o funcionário tiver saldo de férias positivo.
        """
        return self.vacation_balance() > 0

    def pending_compensatory_days(self):
        """
        Retorna os registros de dias compensatórios que ainda não foram usados.
        """
        from vacations.models import CompensatoryDay
        return CompensatoryDay.objects.filter(employee=self, used=False)

    @property
    def compensatory_days_available(self):
        """
        Retorna a contagem de dias compensatórios pendentes de uso.
        """
        return self.pending_compensatory_days().count()

    @property
    def comp_days_taken(self):
        """
        Retorna a quantidade de dias compensatórios já utilizados.
        """
        from vacations.models import CompensatoryDay
        return CompensatoryDay.objects.filter(employee=self, used=True).count()

class AuditLog(models.Model):
    user = models.CharField(max_length=255)
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action} on {self.model_name}"

@property
def active_vacation(self):
    from vacations.models import VacationRequest
    return self.vacationrequest_set.filter(status='A').first()
