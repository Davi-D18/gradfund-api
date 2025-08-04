from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.db.models import Count, Sum, Avg
from apps.authentication.models import CustomerUser
from apps.services.models.services import Service, TypeService
from apps.academic.models.academics import Universidade, Curso


class GradFundAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Estatísticas gerais
        total_usuarios = CustomerUser.objects.count()
        total_estudantes = CustomerUser.objects.filter(tipo_usuario='estudante').count()
        total_servicos = Service.objects.count()
        servicos_ativos = Service.objects.filter(ativo=True).count()
        
        # Top universidades
        top_universidades = (CustomerUser.objects
                           .filter(tipo_usuario='estudante', universidade__isnull=False)
                           .values('universidade__nome')
                           .annotate(count=Count('id'))
                           .order_by('-count')[:5])
        
        # Tipos de serviços mais populares
        top_tipos_servicos = (Service.objects
                            .values('tipo_servico__nome')
                            .annotate(count=Count('id'))
                            .order_by('-count')[:5])
        
        # Preço médio dos serviços
        preco_medio = Service.objects.aggregate(Avg('preco'))['preco__avg'] or 0
        
        extra_context.update({
            'estatisticas': {
                'total_usuarios': total_usuarios,
                'total_estudantes': total_estudantes,
                'total_servicos': total_servicos,
                'servicos_ativos': servicos_ativos,
                'preco_medio': preco_medio / 100 if preco_medio else 0,
            },
            'top_universidades': top_universidades,
            'top_tipos_servicos': top_tipos_servicos,
        })
        
        return super().index(request, extra_context)


# Instância personalizada do admin
admin_site = GradFundAdminSite(name='gradfund_admin')