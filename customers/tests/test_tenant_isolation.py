# customers/tests/test_tenant_isolation.py
from django_tenants.utils import schema_context
from customers.models import Client as TenantClient
from customers.tests import TenantCleanupTestCase
from cms.models import Job


class SchemaIsolationTest(TenantCleanupTestCase):
    """Tests that one recruiter's data never leaks to another"""
    def test_firm_data_isolation(self):
        """Verifies that jobs posted by one firm are invisible to other firms"""
        # Create 2 firms
        firm_a = TenantClient.objects.create(
            schema_name='firm_a', 
            name='Sterling Search'
        )
        firm_b = TenantClient.objects.create(
            schema_name='firm_b', 
            name='Global Talent'
        )
        # Post job in Firm A's schema
        with schema_context(firm_a.schema_name):
            job_a = Job.objects.create(
                title="Investment Banker",
                salary="£150k",
                location="City of London",
                summary="Exclusive high-stakes role.",
                description="Long description here..."
            )
            self.assertEqual(Job.objects.count(), 1)
            job_a_id = job_a.id
        # Switch to Firm B's schema and verify no jobs exist
        with schema_context(firm_b.schema_name):
            # Verify total count is zero in this schema
            self.assertEqual(Job.objects.count(), 0)
            # Try seeing job from wrong schema
            with self.assertRaises(Job.DoesNotExist):
                Job.objects.get(id=job_a_id)
        # Switch back to Firm A and verify job still exists
        with schema_context(firm_a.schema_name):
            self.assertEqual(Job.objects.count(), 1)
            self.assertEqual(Job.objects.first().title, "Investment Banker")