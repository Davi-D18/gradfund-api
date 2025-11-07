import urllib.parse
import requests
from django.conf import settings


class MercadoPagoOAuthService:
    
    @staticmethod
    def get_authorization_url(user_id):
        """Gera URL para autorização do usuário no Mercado Pago"""
        base_url = "https://auth.mercadopago.com.br/authorization"
        
        # Extrair client_id do access_token (formato: APP_USR-xxxx)
        access_token = settings.MERCADOPAGO['ACCESS_TOKEN']
        client_id = access_token.split('-')[1] if '-' in access_token else settings.MERCADOPAGO['PUBLIC_KEY']
        
        params = {
            'client_id': client_id,
            'response_type': 'code',
            'platform_id': 'mp',
            'state': str(user_id),
            'redirect_uri': f"{settings.BASE_URL}/api/v1/payments/oauth/callback/"
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{base_url}?{query_string}"
    
    @staticmethod
    def exchange_code_for_tokens(authorization_code):
        """Troca código de autorização por access_token"""
        url = "https://api.mercadopago.com/oauth/token"
        
        # Extrair client_id do access_token
        access_token = settings.MERCADOPAGO['ACCESS_TOKEN']
        client_id = access_token.split('-')[1] if '-' in access_token else settings.MERCADOPAGO['PUBLIC_KEY']
        
        data = {
            'client_secret': access_token,
            'client_id': client_id,
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': f"{settings.BASE_URL}/api/v1/payments/oauth/callback/"
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            return {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'user_id': token_data['user_id'],
                'expires_in': token_data.get('expires_in')
            }
        else:
            raise Exception(f"Erro ao obter tokens: {response.text}")
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Renova access_token usando refresh_token"""
        url = "https://api.mercadopago.com/oauth/token"
        
        # Extrair client_id do access_token
        access_token = settings.MERCADOPAGO['ACCESS_TOKEN']
        client_id = access_token.split('-')[1] if '-' in access_token else settings.MERCADOPAGO['PUBLIC_KEY']
        
        data = {
            'client_secret': access_token,
            'client_id': client_id,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao renovar token: {response.text}")