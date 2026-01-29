from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils.text import slugify
from django.utils import timezone
from datetime import date, timedelta
import uuid

class Plan(models.Model):
    """Defines what different tiers can do."""
    name = models.CharField(max_length=50) # e.g., 'Free Trial', 'Premium'
    stripe_price_id = models.CharField(max_length=100, blank=True)
    max_jobs = models.IntegerField(default=6)
    can_use_custom_domain = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Client(TenantMixin):
    TEMPLATE_CHOICES = [
        ('executive', 'The Executive'),
        ('startup', 'The Startup'),
        ('boutique', 'The Boutique'),
    ]
    name = models.CharField(max_length=100)
    template_choice = models.CharField(
        max_length=50, 
        choices=TEMPLATE_CHOICES, 
        default='executive'
    )
    
    # --- BUSINESS LOGIC ---
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(default=date.today)
    trial_ends = models.DateField(default=date.today() + timedelta(days=14))
    is_active = models.BooleanField(default=True)

    # Email notification targets (for GDPR-safe applications)
    notification_email_1 = models.EmailField(max_length=255, blank=True, null=True)
    notification_email_2 = models.EmailField(max_length=255, blank=True, null=True)
    
    # Stripe connectivity
    stripe_customer_id = models.CharField(max_length=100, blank=True)

    auto_create_schema = True

    def save(self, *args, **kwargs):
        if not self.schema_name:
            base_slug = slugify(self.name)
            if Client.objects.filter(schema_name=base_slug).exists():
                self.schema_name = f"{base_slug}-{str(uuid.uuid4())[:4]}"
            else:
                self.schema_name = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    pass