import mercadopago
from django.conf import settings
from decimal import Decimal


class MercadoPagoService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO['ACCESS_TOKEN'])
    
    def criar_preferencia(self, payment_data):
        """Cria preferência de pagamento no Mercado Pago"""
        preference_data = {
            "items": [
                {
                    "title": payment_data['titulo'],
                    "quantity": 1,
                    "unit_price": float(payment_data['valor_total']),
                    "currency_id": "BRL"
                }
            ],
            "payer": {
                "name": payment_data['contratante_nome'],
                "email": payment_data['contratante_email']
            },
            "back_urls": {
                "success": payment_data.get('success_url', ''),
                "failure": payment_data.get('failure_url', ''),
                "pending": payment_data.get('pending_url', '')
            },
            "auto_return": "approved",
            "notification_url": payment_data.get('webhook_url', ''),
            "external_reference": str(payment_data['payment_id']),
            "payment_methods": {
                "excluded_payment_types": [],
                "installments": 12
            }
        }
        
        response = self.sdk.preference().create(preference_data)
        return response
    
    def consultar_pagamento(self, payment_id):
        """Consulta status do pagamento no Mercado Pago"""
        response = self.sdk.payment().get(payment_id)
        return response
    
    def validar_webhook(self, request_data):
        """Valida webhook do Mercado Pago"""
        # Implementar validação de assinatura se necessário
        return True
    
    def calcular_split_pagamento(self, valor_total):
        """Calcula divisão do pagamento (7% plataforma, 93% universitário)"""
        valor_total = Decimal(str(valor_total))
        comissao_plataforma = valor_total * Decimal('0.07')
        valor_universitario = valor_total - comissao_plataforma
        
        return {
            'valor_total': valor_total,
            'comissao_plataforma': comissao_plataforma,
            'valor_universitario': valor_universitario
        }