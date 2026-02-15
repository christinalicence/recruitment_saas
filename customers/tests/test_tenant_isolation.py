from django_tenants.utils import schema_context, get_public_schema_name
from customers.models import Client as TenantClient
from customers.tests import TenantTestCase
from cms.models import Job

class SchemaIsolationTest(TenantTestCase):
    def test_firm_data_isolation(self):
        with schema_context(get_public_schema_name()):
            firm_a = TenantClient.objects.create(schema_name='firm-a', name='Sterling Search')
            firm_b = TenantClient.objects.create(schema_name='firm-b', name='Global Talent')

        with schema_context(firm_a.schema_name):
            job_a = Job.objects.create(
                title="Investment Banker", salary="£150k",
                location="London", summary="Role A"
            )
            job_a_id = job_a.id

        with schema_context(firm_b.schema_name):
            self.assertEqual(Job.objects.count(), 0)
            with self.assertRaises(Job.DoesNotExist):
                Job.objects.get(id=job_a_id)