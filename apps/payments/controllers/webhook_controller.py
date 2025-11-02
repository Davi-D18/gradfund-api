from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.payments.services.payment_service import PaymentService
import json


@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_mercadopago(request):
    """Endpoint para receber webhooks do Mercado Pago"""
    try:
        webhook_data = request.data
        
        payment_service = PaymentService()
        webhook = payment_service.processar_webhook(webhook_data)
        
        return Response(
            {'status': 'processed', 'webhook_id': webhook.id}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': 'Erro ao processar webhook'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )