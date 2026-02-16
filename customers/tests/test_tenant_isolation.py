from django_tenants.utils import schema_context, get_public_schema_name
from customers.models import Client as TenantClient
from django_tenants.test.cases import TenantTestCase
from cms.models import Job
from django.db import connection

class SchemaIsolationTest(TenantTestCase):
    
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.schema_name = 'isolation_base_test'
        return tenant

    @classmethod
    def setup_domain(cls, domain):
        domain.domain = 'isolation-base.localhost'
        return domain

    def test_firm_data_isolation(self):
        with schema_context(get_public_schema_name()):
            firm_a = TenantClient.objects.create(schema_name='iso-firm-a', name='Isolation Firm A')
            firm_b = TenantClient.objects.create(schema_name='iso-firm-b', name='Isolation Firm B')

        # Create a job in Firm A
        with schema_context(firm_a.schema_name):
            job_a = Job.objects.create(
                title="Investment Banker", 
                salary="£150k",
                location="London", 
                summary="Role A"
            )
            job_a_id = job_a.id

        # VERIFY: Firm B should see NOTHING from Firm A
        with schema_context(firm_b.schema_name):
            self.assertEqual(Job.objects.count(), 0)
            with self.assertRaises(Job.DoesNotExist):
                Job.objects.get(id=job_a_id)

    def tearDown(self):
        # Reset to public to prevent the 'Flush' error on next test
        connection.set_schema_to_public()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        pass
    