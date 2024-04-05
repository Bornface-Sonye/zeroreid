from django.test import TestCase, Client
from django.urls import reverse
from .models import Suspect, Case, SuspectTestification

class PeaceAppViewsTestCase(TestCase):
    def setUp(self):
        # Set up any necessary data, such as creating instances of models
        Suspect.objects.create(email_address="test@example.com", first_name="John", last_name="Doe", gender="Male", date_of_birth="1990-01-01", drug_test=True, age=30)
        Case.objects.create(case_description="Test case")
        SuspectTestification.objects.create(email_address=Suspect.objects.get(email_address="test@example.com"), case_description=Case.objects.get(case_description="Test case"), answer_1="Answer 1", answer_2="Answer 2")

    def test_home_page_view(self):
        # Test Home page view
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        # Add more assertions if needed

    def test_interrogator_report_view_get(self):
        # Test GET request for Interrogator Report view
        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'interrogator_report.html')
        # Add more assertions if needed

    def test_error_page_view(self):
        # Test Error Page view
        response = self.client.get(reverse('error'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'interrogator_error.html')
        # Add more assertions if needed

    def test_success_page_view(self):
        # Test Success Page view
        response = self.client.get(reverse('success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'interrogator_success.html')
        # Add more assertions if needed

    def test_interrogator_dashboard_view(self):
        # Test Interrogator Dashboard view
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'interrogator_dashboard.html')
        # Add more assertions if needed
