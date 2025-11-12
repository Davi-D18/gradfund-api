import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class KYCValidationService:
    """Serviço para validar nível KYC do usuário no Mercado Pago"""
    
    @staticmethod
    def verificar_kyc_usuario(access_token, user_id):
        """
        Verifica se o usuário tem KYC nível 6 (identificação completa)
        Necessário para receber pagamentos via marketplace
        """
        try:
            url = f"https://api.mercadopago.com/users/{user_id}"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Verificar nível de identificação
                identification_level = user_data.get('identification', {}).get('level', 0)
                
                logger.info(f"Usuário {user_id} - Nível KYC: {identification_level}")
                
                return {
                    'kyc_approved': identification_level >= 6,
                    'identification_level': identification_level,
                    'user_status': user_data.get('status', 'unknown'),
                    'can_receive_payments': identification_level >= 6 and user_data.get('status') == 'active'
                }
            else:
                logger.error(f"Erro ao consultar usuário MP {user_id}: {response.status_code}")
                return {
                    'kyc_approved': False,
                    'identification_level': 0,
                    'error': f'Erro ao consultar dados: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Erro ao verificar KYC: {str(e)}")
            return {
                'kyc_approved': False,
                'identification_level': 0,
                'error': str(e)
            }
    
    @staticmethod
    def get_kyc_requirements():
        """Retorna requisitos para completar KYC"""
        return {
            'nivel_necessario': 6,
            'documentos_necessarios': [
                'Documento de identidade (RG ou CNH)',
                'CPF',
                'Comprovante de endereço',
                'Foto selfie para verificação'
            ],
            'como_completar': 'Acesse o app Mercado Pago > Perfil > Dados pessoais > Completar verificação',
            'tempo_aprovacao': '1-3 dias úteis'
        }