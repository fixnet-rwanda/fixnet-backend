from django.test import TestCase
from core.utils import mask_contact_info


class ContactMaskingTests(TestCase):
    def test_phone_number_masked(self):
        text = "Hello call me at +250788123456 tomorrow"
        masked_text, is_masked = mask_contact_info(text)
        self.assertTrue(is_masked)
        self.assertIn("[Contact hidden until deposit paid]", masked_text)
        self.assertNotIn("+250788123456", masked_text)

    def test_email_masked(self):
        text = "My email is tech@fixnet.rw write to me"
        masked_text, is_masked = mask_contact_info(text)
        self.assertTrue(is_masked)
        self.assertIn("[Email hidden until deposit paid]", masked_text)
