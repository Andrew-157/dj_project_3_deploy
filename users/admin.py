from django.contrib import admin
from django.utils.html import format_html
from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'email', 'date_joined',
        'is_superuser', 'is_active', 'is_staff'
    ]
    list_filter = ['username', 'date_joined']
    search_fields = ['username']
