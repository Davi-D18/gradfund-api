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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        webhook_data = request.data
        logger.info(f"Webhook recebido: {webhook_data}")
        
        # Validar estrutura básica do webhook
        if not webhook_data or not isinstance(webhook_data, dict):
            logger.warning("Webhook inválido: dados ausentes ou formato incorreto")
            return Response({'error': 'Invalid webhook data'}, status=status.HTTP_400_BAD_REQUEST)
        
        event_type = webhook_data.get('type')
        if not event_type:
            logger.warning("Webhook sem tipo de evento")
            return Response({'error': 'Missing event type'}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Processando webhook tipo: {event_type}")
        
        payment_service = PaymentService()
        webhook = payment_service.processar_webhook(webhook_data)
        
        logger.info(f"Webhook processado com sucesso: {webhook.id}")
        
        return Response(
            {
                'status': 'processed', 
                'webhook_id': webhook.id,
                'event_type': event_type,
                'processed': webhook.processado
            }, 
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Erro interno ao processar webhook'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )