from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_notification(request):
    """Endpoint para testar notificações WebSocket"""
    user_id = request.user.customeruser.id
    room_id = request.data.get('room_id', 1)
    
    logger.info(f"🧪 Testando notificação para usuário {user_id}")
    
    channel_layer = get_channel_layer()
    
    # Enviar notificação de teste
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'chat_list_update',
            'room_id': room_id,
            'message': {
                'id': 999,
                'conteudo': 'Mensagem de teste',
                'enviado_em': '2024-01-01T12:00:00Z',
                'remetente': {
                    'id': user_id,
                    'username': 'teste'
                }
            }
        }
    )
    
    logger.info(f"✅ Notificação de teste enviada para user_{user_id}")
    
    return Response({'message': 'Notificação enviada'})