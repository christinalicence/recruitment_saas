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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with schema_context(get_public_schema_name()):
            cls.firm_a = TenantClient.objects.create(
                schema_name='iso-firm-a', name='Isolation Firm A'
            )
            cls.firm_b = TenantClient.objects.create(
                schema_name='iso-firm-b', name='Isolation Firm B'
            )
        cls.firm_a.create_schema(check_if_exists=True)
        cls.firm_b.create_schema(check_if_exists=True)

    @classmethod
    def tearDownClass(cls):
        with connection.cursor() as cursor:
            cursor.execute(f'DROP SCHEMA IF EXISTS "{cls.firm_a.schema_name}" CASCADE')
            cursor.execute(f'DROP SCHEMA IF EXISTS "{cls.firm_b.schema_name}" CASCADE')
        with schema_context(get_public_schema_name()):
            cls.firm_a.delete()
            cls.firm_b.delete()
        super().tearDownClass()

    def test_firm_data_isolation(self):
        with schema_context(self.firm_a.schema_name):
            job_a = Job.objects.create(
                title="Investment Banker",
                salary="£150k",
                location="London",
                summary="Role A"
            )
            job_a_id = job_a.id

        with schema_context(self.firm_b.schema_name):
            self.assertEqual(Job.objects.count(), 0)
            with self.assertRaises(Job.DoesNotExist):
                Job.objects.get(id=job_a_id)

    def tearDown(self):
        connection.set_schema_to_public()
        super().tearDown()
