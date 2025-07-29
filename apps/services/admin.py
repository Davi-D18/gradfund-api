from django.contrib import admin
from apps.services.models.services import TypeService, Service


@admin.register(TypeService)
class TypeServiceAdmin(admin.ModelAdmin):
    list_display = ("nome", "criado_em")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("titulo", "estudante", "tipo_servico", "criado_em", "descricao")
    list_filter = ("tipo_servico", "estudante")