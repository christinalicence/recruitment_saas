from django.test import TransactionTestCase
from django_tenants.utils import get_public_schema_name, schema_context
from customers.models import Client as TenantClient, Domain

class TenantCleanupTestCase(TransactionTestCase):
    """
    Base test case for multi-tenant tests.
    Ensures the public schema exists and wipes extra schemas safely.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with schema_context(get_public_schema_name()):
            public_tenant, created = TenantClient.objects.get_or_create(
                schema_name=get_public_schema_name(),
                defaults={'name': 'Public Schema'}
            )
            Domain.objects.get_or_create(
                domain='localhost',
                defaults={'tenant': public_tenant, 'is_primary': True}
            )

    def tearDown(self):
        """
        Ensures we are in the public schema before deleting tenants.
        """
        super().tearDown()
        # We MUST switch to public to delete other schemas
        with schema_context(get_public_schema_name()):
            tenants_to_delete = TenantClient.objects.exclude(
                schema_name=get_public_schema_name()
            )
            for tenant in tenants_to_delete:
                tenant.delete(force_drop=True)