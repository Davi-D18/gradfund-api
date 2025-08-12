from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.authentication.models import CustomerUser
from apps.services.models.services import Service


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    fields = ('titulo', 'tipo_servico', 'preco', 'ativo')
    readonly_fields = ('titulo', 'tipo_servico', 'preco')
    can_delete = False
    max_num = 5
    verbose_name = "Serviço"
    verbose_name_plural = "Últimos 5 Serviços"


@admin.register(CustomerUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario_link", "status_visual", "tipo_usuario", "universidade", "curso", "ano_formatura", "total_servicos")
    list_filter = ("tipo_usuario", "universidade", "curso", "ano_formatura")

    search_fields = ("usuario__username", "usuario__email",)
    readonly_fields = ("total_servicos", "servicos_ativos", "data_ultimo_servico")
    inlines = [ServiceInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'tipo_usuario',)
        }),
        ('Dados Acadêmicos', {
            'fields': ('universidade', 'curso', 'ano_formatura'),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('total_servicos', 'servicos_ativos', 'data_ultimo_servico'),
            'classes': ('collapse',)
        })
    )
    
    def usuario_link(self, obj):
        return format_html('<a href="{}">{}</a>', 
                          reverse('admin:auth_user_change', args=[obj.usuario.id]), 
                          obj.usuario.username)
    usuario_link.short_description = 'Usuário'
    
    def status_visual(self, obj):
        if obj.usuario.is_active:
            color = 'green' if obj.tipo_usuario == 'estudante' else 'blue'
            return format_html('<span style="color: {};">● Ativo</span>', color)
        return format_html('<span style="color: red;">● Inativo</span>')
    status_visual.short_description = 'Status'
    
    def total_servicos(self, obj):
        count = obj.services_customer_user.count()
        return format_html('<strong>{}</strong>', count)
    total_servicos.short_description = 'Total Serviços'
    
    def servicos_ativos(self, obj):
        count = obj.services_customer_user.filter(ativo=True).count()
        return format_html('<span style="color: green;">{}</span>', count)
    servicos_ativos.short_description = 'Serviços Ativos'
    
    def data_ultimo_servico(self, obj):
        ultimo = obj.services_customer_user.order_by('-criado_em').first()
        if ultimo:
            return ultimo.criado_em.strftime('%d/%m/%Y')
        return '-'
    data_ultimo_servico.short_description = 'Último Serviço'