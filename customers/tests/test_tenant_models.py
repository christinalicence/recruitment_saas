from django_tenants.test.cases import TenantTestCase
from customers.models import Client
from django.utils.text import slugify
from django_tenants.utils import schema_context, get_public_schema_name
from django.db import connection


class ClientModelTest(TenantTestCase):
    """
    Tests the custom save logic and slug generation for the Client model.
    """
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.schema_name = 'models_test_schema'
        return tenant

    @classmethod
    def setup_domain(cls, domain):
        domain.domain = 'models-test.localhost'
        return domain

    def test_auto_schema_name_generation(self):
        with schema_context(get_public_schema_name()):
            tenant = Client.objects.create(name="Unique Sterling Search")
        self.assertEqual(tenant.schema_name, slugify("Unique Sterling Search"))

    def test_unique_slug_collision_handling(self):
        with schema_context(get_public_schema_name()):
            Client.objects.create(name="Collision Test")
            tenant2 = Client.objects.create(name="Collision Test")
        self.assertTrue(tenant2.schema_name.startswith("collision-test-"))
        self.assertNotEqual(tenant2.schema_name, "collision-test")

    def tearDown(self):
        connection.set_schema_to_public()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        pass
