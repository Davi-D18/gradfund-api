from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from jwt import decode as jwt_decode
from django.conf import settings


@api_view(['POST'])
def debug_token(request):
    """Debug do token enviado pelo frontend"""
    token = request.data.get('token', '')
    
    if not token:
        return Response({'error': 'Token não fornecido'})
    
    try:
        decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        return Response({
            'token_valid': True,
            'user_id': decoded_data.get('user_id'),
            'username': decoded_data.get('username'),
            'tipo_usuario': decoded_data.get('tipo_usuario'),
            'exp': decoded_data.get('exp'),
            'iat': decoded_data.get('iat')
        })
        
    except Exception as e:
        return Response({
            'token_valid': False,
            'error': str(e)
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_current_user_api(request):
    """Verifica qual usuário está autenticado via API REST"""
    return Response({
        'user_id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'is_authenticated': True
    })