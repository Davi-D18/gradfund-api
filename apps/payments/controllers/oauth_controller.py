from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.payments.services.oauth_service import MercadoPagoOAuthService
from apps.payments.services.kyc_validation_service import KYCValidationService
from django.contrib.auth.models import User
import logging


logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_oauth_url(request):
    """Retorna URL para conectar conta do Mercado Pago"""
    try:
        # Verificar se usuário é universitário
        if request.user.usuario_user.tipo_usuario != 'universitario':
            return JsonResponse({
                'error': 'Apenas universitários podem conectar conta do Mercado Pago'
            }, status=403)
        
        # Verificar se já está conectado
        if request.user.usuario_user.mp_access_token:
            return JsonResponse({
                'is_connected': True,
                'mp_user_id': request.user.usuario_user.mp_user_id,
                'message': 'Conta já conectada ao Mercado Pago'
            })
        
        oauth_service = MercadoPagoOAuthService()
        auth_url = oauth_service.get_authorization_url(request.user.id)
        
        return JsonResponse({
            'authorization_url': auth_url,
            'message': 'Abra esta URL no navegador para conectar sua conta'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def oauth_callback(request):
    """Processa callback do Mercado Pago"""
    try:
        code = request.GET.get('code')
        state = request.GET.get('state')  # user_id
        error = request.GET.get('error')
        
        if error:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/error?error={error}")
        
        if not code or not state:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/error?error=missing_params")
        
        # Trocar código por tokens
        oauth_service = MercadoPagoOAuthService()
        tokens = oauth_service.exchange_code_for_tokens(code)
        
        # Validar KYC do usuário
        kyc_result = KYCValidationService.verificar_kyc_usuario(
            tokens['access_token'], 
            tokens['user_id']
        )
        
        # Salvar tokens no usuário
        user = User.objects.get(id=state)
        customer_user = user.usuario_user
        
        customer_user.mp_access_token = tokens['access_token']
        customer_user.mp_refresh_token = tokens.get('refresh_token')
        customer_user.mp_user_id = tokens['user_id']
        customer_user.save()
        
        # Verificar se KYC é suficiente
        if not kyc_result['kyc_approved']:
            logger.warning(f"Usuário {user.username} conectou MP mas KYC insuficiente: nível {kyc_result['identification_level']}")
        
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        # Redirecionar com informações de KYC
        if kyc_result['kyc_approved']:
            return redirect(f"{frontend_url}/success?connected=true&kyc=approved")
        else:
            return redirect(f"{frontend_url}/success?connected=true&kyc=pending&level={kyc_result['identification_level']}")
        
    except Exception as e:
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/error?error=oauth_failed&message={str(e)}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_mp_connection(request):
    """Verifica se usuário tem conta MP conectada e status KYC"""
    try:
        customer_user = request.user.usuario_user
        
        is_connected = bool(customer_user.mp_access_token)
        
        response_data = {
            'is_connected': is_connected,
            'mp_user_id': customer_user.mp_user_id if is_connected else None,
        }
        
        if is_connected:
            # Verificar status KYC atual
            kyc_result = KYCValidationService.verificar_kyc_usuario(
                customer_user.mp_access_token,
                customer_user.mp_user_id
            )
            
            response_data.update({
                'kyc_approved': kyc_result['kyc_approved'],
                'identification_level': kyc_result['identification_level'],
                'can_create_services': kyc_result['kyc_approved'],
                'message': 'Conta conectada e KYC aprovado' if kyc_result['kyc_approved'] else f'Conta conectada mas KYC pendente (nível {kyc_result["identification_level"]})',
                'kyc_requirements': KYCValidationService.get_kyc_requirements() if not kyc_result['kyc_approved'] else None
            })
        else:
            response_data['message'] = 'Conta não conectada'
        
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disconnect_mp_account(request):
    """Desconecta conta do Mercado Pago"""
    try:
        customer_user = request.user.usuario_user
        
        # Limpar tokens
        customer_user.mp_access_token = None
        customer_user.mp_refresh_token = None
        customer_user.mp_user_id = None
        customer_user.save()
        
        return JsonResponse({
            'message': 'Conta do Mercado Pago desconectada com sucesso'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)