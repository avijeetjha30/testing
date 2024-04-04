from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.account.models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'is_active', 'created_at', 'updated_at')
    ordering = ('-updated_at',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(User, CustomUserAdmin)
