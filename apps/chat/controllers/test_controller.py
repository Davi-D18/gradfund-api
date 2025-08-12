from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_chat_notification(request):
    """Endpoint para testar notificações de chat"""
    
    user_id = request.user.usuario_user.id
    channel_layer = get_channel_layer()
    
    # Enviar notificação de teste
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'chat_list_update',
            'room_id': 999,
            'message_id': 999,
            'content': 'Mensagem de teste via API',
            'sender_id': 1,
            'timestamp': '2024-01-01T10:00:00Z'
        }
    )
    
    return Response({
        'message': f'Notificação de teste enviada para usuário {user_id}',
        'user_id': user_id
    })