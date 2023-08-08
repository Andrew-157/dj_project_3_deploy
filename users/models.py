from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models


def validate_file_size(file):
    # As image field was removed for CustomUser
    # this function is not necessary for functionality of the app
    # but when removed the following error is raised in initial migration
    # of users app: AttributeError: module 'users.models' has no attribute 'validate_file_size'
    max_kb_size = 500

    if file.size > max_kb_size * 1024:
        raise ValidationError(f'Files cannot be larger than {max_kb_size}KB')


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
