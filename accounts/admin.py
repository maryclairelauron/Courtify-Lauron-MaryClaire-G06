from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Courtify', {'fields': ('role', 'contact_number', 'profile_photo')}),
    )
    list_display = ('username', 'email', 'role', 'is_active')