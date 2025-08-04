from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from apps.services.models.services import TypeService, Service


@admin.register(TypeService)
class TypeServiceAdmin(admin.ModelAdmin):
    list_display = ("nome", "total_servicos", "criado_em")
    search_fields = ("nome",)
    
    def total_servicos(self, obj):
        count = obj.services_type_service.count()
        return format_html('<strong>{}</strong>', count)
    total_servicos.short_description = 'Total Serviços'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("titulo", "universitario_link", "tipo_servico", "preco", "status_visual", "criado_em")
    list_filter = ("tipo_servico", "ativo", "criado_em")
    search_fields = ("titulo", "estudante__usuario__username", "descricao")
    list_per_page = 25
    actions = ['ativar_servicos', 'desativar_servicos',]
    
    fieldsets = (
        ('Informações do Serviço', {
            'fields': ('titulo', 'descricao', 'tipo_servico')
        }),
        ('Preço e Status', {
            'fields': ('preco', 'ativo')
        }),
        ('Universitário', {
            'fields': ('estudante',)
        })
    )
    
    def universitario_link(self, obj):
        return format_html('<a href="{}">{}</a>', 
                          reverse('admin:authentication_customeruser_change', args=[obj.estudante.id]), 
                          obj.estudante.usuario.username)
    universitario_link.short_description = 'Universitário'
    

    
    def status_visual(self, obj):
        if obj.ativo:
            return format_html('<span style="color: green;">● Ativo</span>')
        return format_html('<span style="color: red;">● Inativo</span>')
    status_visual.short_description = 'Status'
    status_visual.admin_order_field = 'ativo'

    @admin.action(description='Ativar serviços selecionados')
    def ativar_servicos(self, request, queryset):
        updated = queryset.update(ativo=True)
        messages.success(request, f'{updated} serviços foram ativados.')

    @admin.action(description='Desativar serviços selecionados')
    def desativar_servicos(self, request, queryset):
        updated = queryset.update(ativo=False)
        messages.success(request, f'{updated} serviços foram desativados.')