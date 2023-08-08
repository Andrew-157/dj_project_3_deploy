from django.test import TestCase

from users.forms import EmailLoginForm, UserCreationForm, UserChangeForm


class EmailLoginFormTest(TestCase):

    def test_username_label(self):
        form = EmailLoginForm()
        field_label = form.fields['username'].label
        self.assertEqual(field_label, 'Email')


class UserCreationFormTest(TestCase):

    def test_email_help_text(self):
        form = UserCreationForm()
        help_text = form.fields['email'].help_text
        self.assertEqual(help_text, 'Required. Enter a valid email address.')


class UserChangeFormTest(TestCase):

    def test_email_help_text(self):
        form = UserChangeForm()
        help_text = form.fields['email'].help_text
        self.assertEqual(help_text, 'Required. Enter a valid email address.')
