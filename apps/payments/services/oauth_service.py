import requests
from django.conf import settings
from urllib.parse import urlencode


class MercadoPagoOAuthService:
    """Serviço para OAuth do Mercado Pago - obter tokens dos universitários"""
    
    def get_authorization_url(self, user_id):
        """Gera URL para autorização OAuth"""
        params = {
            'client_id': settings.MERCADOPAGO['APPLICATION_ID'],
            'response_type': 'code',
            'platform_id': 'mp',
            'redirect_uri': f"{settings.BASE_URL}/api/v1/payments/oauth/callback/",
            'state': str(user_id)  # ID do universitário
        }
        
        base_url = "https://auth.mercadopago.com.br/authorization"
        return f"{base_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code):
        """Troca código por access_token"""
        data = {
            'client_id': settings.MERCADOPAGO['APPLICATION_ID'],
            'client_secret': settings.MERCADOPAGO['CLIENT_SECRET'],
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': f"{settings.BASE_URL}/api/v1/payments/oauth/callback/"
        }
        
        response = requests.post(
            'https://api.mercadopago.com/oauth/token',
            json=data
        )
        
        return response.json()