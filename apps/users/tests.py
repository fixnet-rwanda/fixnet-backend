from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_otp_request(self):
        url = reverse("otp-request")
        response = self.client.post(url, {"phone_number": "+250788123456", "channel": "sms"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")

    def test_otp_verify_creates_user(self):
        url = reverse("otp-verify")
        response = self.client.post(url, {"phone_number": "+250788123456", "code": "123456"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.data)
        self.assertTrue(User.objects.filter(phone_number="+250788123456").exists())
