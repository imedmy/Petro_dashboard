from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('معلومات إضافية', {'fields': ('phone', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('معلومات إضافية', {'fields': ('phone', 'address')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)