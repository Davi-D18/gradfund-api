import mercadopago
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class MercadoPagoService:
    def __init__(self, access_token=None):
        token = access_token or settings.MERCADOPAGO['ACCESS_TOKEN']
        if not token:
            raise ValueError("Token do Mercado Pago não configurado")
        self.sdk = mercadopago.SDK(token)
    
    def criar_preferencia(self, payment_data):
        """Cria preferência de pagamento no Mercado Pago"""
        try:
            # Validar dados obrigatórios
            required_fields = ['titulo', 'valor_total', 'contratante_nome', 'contratante_email', 'payment_id']
            for field in required_fields:
                if not payment_data.get(field):
                    raise ValueError(f"Campo obrigatório ausente: {field}")
            
            preference_data = {
                "items": [
                    {
                        "title": str(payment_data['titulo'])[:256],  # Limitar título
                        "quantity": 1,
                        "unit_price": float(payment_data['valor_total']),
                        "currency_id": "BRL"
                    }
                ],
                "payer": {
                    "name": str(payment_data['contratante_nome'])[:256],
                    "email": str(payment_data['contratante_email'])
                },
                "back_urls": {
                    "success": payment_data.get('success_url', f"{settings.FRONTEND_URL}/pagamentos/sucesso"),
                    "failure": payment_data.get('failure_url', f"{settings.FRONTEND_URL}/pagamentos/erro"),
                    "pending": payment_data.get('pending_url', f"{settings.FRONTEND_URL}/pagamentos/pendente"),
                },
                "external_reference": str(payment_data['payment_id']),
                "binary_mode": False,
                "expires": False,  # Não expira
                "payment_methods": {
                    "excluded_payment_types": [],
                    "excluded_payment_methods": [],
                    "installments": 12  # Máximo 12 parcelas
                }
            }
            
            # Adicionar notification_url apenas se fornecido
            if payment_data.get('webhook_url'):
                preference_data["notification_url"] = payment_data['webhook_url']
            
            # Implementar marketplace_fee com OAuth
            comissao_plataforma = payment_data.get('comissao_plataforma')
            if comissao_plataforma and float(comissao_plataforma) > 0:
                preference_data["marketplace_fee"] = float(comissao_plataforma)
            
            logger.info(f"Criando preferência MP para payment_id: {payment_data['payment_id']}")
            response = self.sdk.preference().create(preference_data)
            
            if response.get('status') != 201:
                logger.error(f"Erro ao criar preferência MP: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao criar preferência: {str(e)}")
            raise
    
    def consultar_pagamento(self, payment_id):
        """Consulta status do pagamento no Mercado Pago"""
        try:
            response = self.sdk.payment().get(payment_id)
            if response.get('status') != 200:
                logger.error(f"Erro ao consultar pagamento {payment_id}: {response}")
            return response
        except Exception as e:
            logger.error(f"Erro ao consultar pagamento {payment_id}: {str(e)}")
            raise
    
    def validar_webhook(self, request_data):
        """Valida webhook do Mercado Pago"""
        try:
            # Validação básica da estrutura do webhook
            if not isinstance(request_data, dict):
                return False
            
            required_fields = ['type', 'data']
            for field in required_fields:
                if field not in request_data:
                    logger.warning(f"Campo obrigatório ausente no webhook: {field}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Erro ao validar webhook: {str(e)}")
            return False
    
    def calcular_split_pagamento(self, valor_total):
        """Calcula divisão do pagamento (7% plataforma, 93% universitário)"""
        valor_total = Decimal(str(valor_total))
        comissao_plataforma = valor_total * Decimal('0.07')
        valor_universitario = valor_total - comissao_plataforma
        
        return {
            'valor_total': valor_total,
            'comissao_plataforma': comissao_plataforma.quantize(Decimal('0.01')),
            'valor_universitario': valor_universitario.quantize(Decimal('0.01'))
        }