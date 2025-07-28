from django.contrib import admin
from apps.services.models.services import TypeService


@admin.register(TypeService)
class TypeServiceAdmin(admin.ModelAdmin):
    list_display = ("nome", "criado_em")