
from . import TenantCleanupTestCase
from customers.models import Client
from django.utils.text import slugify

class ClientModelTest(TenantCleanupTestCase):
    def test_auto_schema_name_generation(self):
        """
        Test that providing only a company name automatically 
        populates the schema_name (subdomain) on save.
        """
        tenant = Client.objects.create(
            name="Sterling Search & Selection",
            template_choice="executive"
        )
        expected_slug = slugify("Sterling Search & Selection") # sterling-search-selection
        self.assertEqual(tenant.schema_name, expected_slug)

    def test_unique_slug_collision_handling(self):
        """
        Test that if two different clients have the same name,
        the model generates unique schema names to avoid database errors.
        """
        Client.objects.create(name="Alpha Recruitment")
        # Create a second one with the same name
        tenant2 = Client.objects.create(name="Alpha Recruitment")
        # Verify they didn't collide
        self.assertNotEqual(tenant2.schema_name, "alpha-recruitment")
        self.assertTrue(tenant2.schema_name.startswith("alpha-recruitment-"))