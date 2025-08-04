from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from apps.authentication.models import CustomerUser
from apps.services.models.services import Service, TypeService


@staff_member_required
def admin_stats_api(request):
    """API para fornecer estatísticas do dashboard"""
    try:
        # Estatísticas básicas
        total_usuarios = CustomerUser.objects.count()
        total_estudantes = CustomerUser.objects.filter(tipo_usuario='estudante').count()
        total_servicos = Service.objects.count()
        servicos_ativos = Service.objects.filter(ativo=True).count()
        
        # Top universidades
        top_universidades = list(
            CustomerUser.objects
            .filter(tipo_usuario='estudante', universidade__isnull=False)
            .values('universidade__nome')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        # Tipos de serviços mais populares
        top_tipos_servicos = list(
            Service.objects
            .values('tipo_servico__nome')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        return JsonResponse({
            'total_usuarios': total_usuarios,
            'total_estudantes': total_estudantes,
            'total_servicos': total_servicos,
            'servicos_ativos': servicos_ativos,
            'top_universidades': top_universidades,
            'top_tipos_servicos': top_tipos_servicos,
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'total_usuarios': 0,
            'total_estudantes': 0,
            'total_servicos': 0,
            'servicos_ativos': 0,
            'top_universidades': [],
            'top_tipos_servicos': [],
        }, status=500)