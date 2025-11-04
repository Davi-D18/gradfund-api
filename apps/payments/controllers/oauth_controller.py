from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.payments.services.oauth_service import MercadoPagoOAuthService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_oauth_url(request):
    """Gera URL OAuth para universitário conectar conta MP"""
    if request.user.usuario_user.tipo_usuario != 'universitario':
        return Response(
            {'error': 'Apenas universitários podem conectar conta MP'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    oauth_service = MercadoPagoOAuthService()
    auth_url = oauth_service.get_authorization_url(request.user.usuario_user.id)
    
    return Response({'auth_url': auth_url})


@api_view(['GET'])
@permission_classes([])
def oauth_callback(request):
    """Callback OAuth - recebe código e troca por token"""
    code = request.GET.get('code')
    state = request.GET.get('state')  # user_id
    
    if not code or not state:
        return Response({'error': 'Parâmetros inválidos'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from apps.authentication.models import CustomerUser
        user_profile = CustomerUser.objects.get(id=state)
        
        oauth_service = MercadoPagoOAuthService()
        token_data = oauth_service.exchange_code_for_token(code)
        
        if 'access_token' in token_data:
            user_profile.mp_access_token = token_data['access_token']
            user_profile.mp_refresh_token = token_data.get('refresh_token')
            user_profile.mp_user_id = token_data.get('user_id')
            user_profile.save()
            
            return Response({'message': 'Conta conectada com sucesso!'})
        else:
            return Response({'error': 'Erro ao obter token'}, status=status.HTTP_400_BAD_REQUEST)
            
    except CustomerUser.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)