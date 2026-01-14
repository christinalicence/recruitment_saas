from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils.text import slugify
from datetime import date
import uuid


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    template_choice = models.CharField(max_length=50, default='modern')
    auto_create_schema = True
    on_trial = models.BooleanField(default=False)
    paid_until = models.DateField(null=True, blank=True)
    created_on = models.DateField(default=date.today)

    def save(self, *args, **kwargs):
        # If no schema_name is provided, generate one from the name
        if not self.schema_name:
            base_slug = slugify(self.name)
            # Handle clashes if the name is already taken
            if Client.objects.filter(schema_name=base_slug).exists():
                self.schema_name = f"{base_slug}-{str(uuid.uuid4())[:4]}"
            else:
                self.schema_name = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass
