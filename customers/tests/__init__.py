from django.test import TransactionTestCase
from django_tenants.utils import get_public_schema_name
from customers.models import Client as TenantClient, Domain


class TenantCleanupTestCase(TransactionTestCase):
    """
    Base class that ensures tenant schemas are cleaned up after each test.
    All tenant-related tests inherit from this class.
    It is called in multiple test files, so placed here for reuse.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure public tenant exists with domain
        public_tenant, created = TenantClient.objects.get_or_create(
            schema_name=get_public_schema_name(),
            defaults={'name': 'Public Schema'}
        )
        # Ensure localhost domain exists for public tenant
        Domain.objects.get_or_create(
            domain='localhost',
            defaults={'tenant': public_tenant, 'is_primary': True}
        )
    
    def tearDown(self):
        super().tearDown()
        # Clean up all tenant schemas except 'public'
        for tenant in TenantClient.objects.exclude(schema_name='public'):
            try:
                tenant.delete(force_drop=True)
            except Exception as e:
                print(f"Warning: Could not delete tenant {tenant.schema_name}: {e}")