from . import TenantCleanupTestCase
from customers.models import Client
from django.utils.text import slugify
from django_tenants.utils import schema_context, get_public_schema_name

class ClientModelTest(TenantCleanupTestCase):
    def test_auto_schema_name_generation(self):
        with schema_context(get_public_schema_name()):
            tenant = Client.objects.create(name="Sterling Search & Selection")
        self.assertEqual(tenant.schema_name, slugify("Sterling Search & Selection"))

    def test_unique_slug_collision_handling(self):
        with schema_context(get_public_schema_name()):
            Client.objects.create(name="Alpha Recruitment")
            tenant2 = Client.objects.create(name="Alpha Recruitment")
        self.assertTrue(tenant2.schema_name.startswith("alpha-recruitment-"))