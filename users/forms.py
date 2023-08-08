import re
from django import forms
from users.models import CustomUser
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm,\
    UserChangeForm as BaseUserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError


class UserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(required=True,
                             help_text='Required. Enter a valid email address.')

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2'
        ]

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')

        if username and len(username) < 6:
            msg = 'Username cannot be shorter than 6 characters.'
            self.add_error('username', msg)

        return cleaned_data


class UserChangeForm(BaseUserChangeForm):
    email = forms.EmailField(required=True,
                             help_text='Required. Enter a valid email address.')
    password = None

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email'
        ]

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')

        if username and len(username) < 6:
            msg = 'Username cannot be shorter than 6 characters.'
            self.add_error('username', msg)

        return cleaned_data


class EmailLoginForm(AuthenticationForm):
    # email = forms.EmailField(
    #     widget=forms.EmailInput(attrs={'autofocus': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.error_messages = {
            'invalid_login': "Please enter a correct email and password. Note that both fields may be case-sensitive.",
            'inactive': "This account is inactive.",
        }
        # self.fields['password'].widget.attrs['placeholder'] = 'Password'

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if email and password:
            self.cleaned_data['email'] = email.lower()

        return self.cleaned_data
