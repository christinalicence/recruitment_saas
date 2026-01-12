from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from datetime import date

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    template_choice = models.CharField(max_length=50, default='modern')
    auto_create_schema = True
    on_trial = models.BooleanField(default=False)
    paid_until = models.DateField(null=True, blank=True)
    created_on = models.DateField(default=date.today)

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    pass
