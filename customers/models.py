from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils.text import slugify
from datetime import date, timedelta
import uuid

class Plan(models.Model):
    """The 'Standard' plan for the MVP."""
    name = models.CharField(max_length=50, default="Standard")
    stripe_price_id = models.CharField(max_length=100, blank=True)
    max_jobs = models.IntegerField(default=6)

    def __str__(self):
        return self.name

class Client(TenantMixin):
    TEMPLATE_CHOICES = [
        ('executive', 'The Executive'),
        ('startup', 'The Startup'),
        ('boutique', 'The Boutique'),
    ]
    name = models.CharField(max_length=100)
    template_choice = models.CharField(max_length=50, choices=TEMPLATE_CHOICES, default='executive')
    
    # Subscription tracking
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(default=date.today)
    trial_ends = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    # Notification Emails
    master_email = models.EmailField(blank=True, null=True)
    notification_email_1 = models.EmailField(max_length=255, blank=True, null=True)
    notification_email_2 = models.EmailField(max_length=255, blank=True, null=True)
    
    stripe_customer_id = models.CharField(max_length=100, blank=True)

    auto_create_schema = True

    @property
    def is_on_trial(self):
        """Returns True if the trial hasn't expired yet."""
        if self.trial_ends:
            return date.today() <= self.trial_ends
        return False

    def save(self, *args, **kwargs):
        if not self.trial_ends:
            self.trial_ends = date.today() + timedelta(days=14)
            
        if not self.schema_name:
            base_slug = slugify(self.name)
            if Client.objects.filter(schema_name=base_slug).exists():
                self.schema_name = f"{base_slug}-{str(uuid.uuid4())[:4]}"
            else:
                self.schema_name = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# The Domain model is required by django-tenants
class Domain(DomainMixin):
    pass
