from django.test import TransactionTestCase
from customers.models import Client as TenantClient


class TenantCleanupTestCase(TransactionTestCase):
    """
    Base class that ensures tenant schemas are cleaned up after each test.
    All tenant-related tests inherit from this class.
    It is called in multiple test files, so placed here for reuse.
    """
    def tearDown(self):
        super().tearDown()
        # Clean up all tenant schemas except 'public'
        for tenant in TenantClient.objects.exclude(schema_name='public'):
            try:
                tenant.delete(force_drop=True)
            except Exception as e:
                print(f"Warning: Could not delete tenant {tenant.schema_name}: {e}")
