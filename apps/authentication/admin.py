from django.contrib import admin
from apps.authentication.models import CustomerUser


@admin.register(CustomerUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "tipo_usuario", "universidade", "curso", "ano_formatura")
    list_filter = ("tipo_usuario",)