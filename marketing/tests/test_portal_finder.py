import uuid
from django.test import TestCase, Client as TestClient
from django.urls import clear_url_caches, set_urlconf
from django.conf import settings
from django_tenants.utils import schema_context, get_public_schema_name
from customers.models import Client as TenantClient, Domain


class PortalFinderTest(TestCase):
    """
    Tests for the /find-portal/ view.
    Portal finder queries Client.notification_email_1 which lives in the
    public schema, so plain TestCase is sufficient — no TenantTestCase needed.
    Follows the same setup pattern as test_onboarding.py.
    """

    @classmethod
    def setUpTestData(cls):
        with schema_context(get_public_schema_name()):
            cls.public_tenant, _ = TenantClient.objects.get_or_create(
                schema_name='public',
                defaults={'name': 'Public'},
            )
            domain, created = Domain.objects.get_or_create(
                domain='testserver',
                defaults={'tenant': cls.public_tenant, 'is_primary': True},
            )
            if not created and domain.tenant != cls.public_tenant:
                domain.tenant = cls.public_tenant
                domain.save()
            uid = str(uuid.uuid4())[:4]
            cls.agency = TenantClient.objects.create(
                schema_name=f'finder-agency-{uid}',
                name='Finder Agency',
                notification_email_1='hello@finderagency.com',
            )
            cls.agency_domain = Domain.objects.create(
                domain='finder-agency.getpillarpost.com',
                tenant=cls.agency,
                is_primary=True,
            )

    def setUp(self):
        clear_url_caches()
        set_urlconf(settings.PUBLIC_SCHEMA_URLCONF)
        self.client = TestClient()

    def test_portal_found_by_exact_email(self):
        """POSTing a matching email returns the tenant's login URL in the response."""
        response = self.client.post(
            '/find-portal/',
            {'email': 'hello@finderagency.com'},
            HTTP_HOST='testserver',
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'finder-agency.getpillarpost.com')

    def test_portal_not_found_shows_error(self):
        """POSTing an unknown email renders the page with an error message."""
        response = self.client.post(
            '/find-portal/',
            {'email': 'nobody@unknown.com'},
            HTTP_HOST='testserver',
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No portals found')

    def test_email_lookup_is_case_insensitive(self):
        """Portal finder must find a tenant regardless of the submitted email case."""
        response = self.client.post(
            '/find-portal/',
            {'email': 'HELLO@FINDERAGENCY.COM'},
            HTTP_HOST='testserver',
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'finder-agency.getpillarpost.com')

    def test_post_with_empty_email_does_not_crash(self):
        """POSTing with an empty email string should render the form cleanly."""
        response = self.client.post(
            '/find-portal/',
            {'email': ''},
            HTTP_HOST='testserver',
        )
        self.assertEqual(response.status_code, 200)

    def test_get_request_renders_form(self):
        """GET /find-portal/ should render the finder form with a 200."""
        response = self.client.get('/find-portal/', HTTP_HOST='testserver')
        self.assertEqual(response.status_code, 200)

    def test_email_with_leading_trailing_whitespace_still_finds_portal(self):
        """The view strips whitespace from the submitted email before querying."""
        response = self.client.post(
            '/find-portal/',
            {'email': '  hello@finderagency.com  '},
            HTTP_HOST='testserver',
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'finder-agency.getpillarpost.com')

    def tearDown(self):
        set_urlconf(None)
        clear_url_caches()