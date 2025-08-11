from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_current_user(request):
    """Endpoint para verificar qual usuário está autenticado"""
    user = request.user
    
    return Response({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'is_authenticated': user.is_authenticated,
        'token_info': 'Token válido e usuário identificado corretamente'
    })


@api_view(['GET'])
def debug_all_users(request):
    """Endpoint para listar todos os usuários (para debug)"""
    users = User.objects.all().values('id', 'username', 'email', 'is_active')
    
    return Response({
        'total_users': len(users),
        'users': list(users)
    })