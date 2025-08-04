from django.db.models import Count
from apps.authentication.models import CustomerUser
from apps.services.models.services import Service


def dashboard_context(request):
    """Context processor para adicionar dados do dashboard"""
    if not request.path == '/admin/':
        return {}
    
    # Estatísticas básicas
    total_usuarios = CustomerUser.objects.count()
    total_estudantes = CustomerUser.objects.filter(tipo_usuario='universitario').count()
    total_servicos = Service.objects.count()
    servicos_ativos = Service.objects.filter(ativo=True).count()
    
    # Top universidades
    top_universidades = (CustomerUser.objects
                       .filter(tipo_usuario='universitario', universidade__isnull=False)
                       .values('universidade__nome')
                       .annotate(count=Count('id'))
                       .order_by('-count')[:5])
    
    # Tipos de serviços mais populares
    top_tipos_servicos = (Service.objects
                        .values('tipo_servico__nome')
                        .annotate(count=Count('id'))
                        .order_by('-count')[:5])
    
    return {
        'dashboard_stats': {
            'total_usuarios': total_usuarios,
            'total_estudantes': total_estudantes,
            'total_servicos': total_servicos,
            'servicos_ativos': servicos_ativos,
        },
        'top_universidades': list(top_universidades),
        'top_tipos_servicos': list(top_tipos_servicos),
    }