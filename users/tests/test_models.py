from django.test import TestCase

from users.models import CustomUser


class CustomUserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        CustomUser.objects.create_user(username="antonio",
                                       email="antonio@gmail.com",
                                       password="34somepassword34")

    def test_email_label(self):
        user = CustomUser.objects.get(username='antonio')
        field_label = user._meta.get_field('email').verbose_name
        self.assertEqual(field_label, 'email')
