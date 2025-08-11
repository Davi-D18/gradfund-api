from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from ..consumers.chat_consumer import active_connections


@api_view(['GET'])
@permission_classes([IsAdminUser])
def websocket_status(request):
    """Endpoint para monitorar conexões WebSocket ativas (apenas admin)"""
    connections_detail = []
    for key, connection_data in active_connections.items():
        if isinstance(connection_data, dict):
            connections_detail.append({
                'key': key,
                'user_id': connection_data.get('user_id'),
                'username': connection_data.get('username'),
                'room_id': connection_data.get('room_id'),
                'channel': connection_data.get('channel')
            })
        else:
            # Compatibilidade com formato antigo
            parts = key.split('_')
            if len(parts) >= 4:
                connections_detail.append({
                    'key': key,
                    'user_id': parts[1],
                    'room_id': parts[3],
                    'channel': connection_data
                })
    
    return Response({
        'active_connections': len(active_connections),
        'connections': connections_detail
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def clear_websocket_connections(request):
    """Endpoint para limpar todas as conexões WebSocket (apenas admin)"""
    count = len(active_connections)
    connections_before = []
    
    for key, connection_data in active_connections.items():
        if isinstance(connection_data, dict):
            connections_before.append({
                'key': key,
                'user_id': connection_data.get('user_id'),
                'username': connection_data.get('username')
            })
        else:
            connections_before.append({'key': key})
    
    active_connections.clear()
    
    return Response({
        'message': f'{count} conexões WebSocket limpas com sucesso',
        'cleared_count': count,
        'connections_cleared': connections_before
    }, status=status.HTTP_200_OK)