from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from apps.chat.models.chat import ChatRoom, Message
from apps.chat.schemas.chat_schema import MessageSerializer
from apps.chat.services.chat_service import ChatService


class MessagePagination(PageNumberPagination):
    """Paginação personalizada para mensagens"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualizar mensagens (somente leitura via API)"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination
    
    def get_queryset(self):
        """Retorna mensagens da sala especificada"""
        room_id = self.kwargs.get('room_pk')
        if room_id:
            # Verificar se usuário tem acesso à sala usando service
            sala = get_object_or_404(ChatRoom, id=room_id)
            
            customer_user = self.request.user.usuario_user
            if not ChatService.verificar_permissao_sala(sala, customer_user):
                return Message.objects.none()
            
            return Message.objects.filter(
                sala_chat=sala
            ).select_related('remetente').order_by('-enviado_em')
        
        return Message.objects.none()
    
    @action(detail=True, methods=['patch'])
    def marcar_lida(self, request, room_pk=None, pk=None):
        """Marca uma mensagem como lida"""
        mensagem = self.get_object()
        
        # Só pode marcar como lida se não for o remetente
        customer_user = request.user.usuario_user
        if mensagem.remetente != customer_user:
            if not mensagem.lida:
                mensagem.lida = True
                mensagem.save()
                return Response(
                    {'message': 'Mensagem marcada como lida'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'message': 'Mensagem já estava marcada como lida'},
                    status=status.HTTP_200_OK
                )
        
        # Se for própria mensagem, retornar sucesso sem fazer nada
        return Response(
            {'message': 'Próprias mensagens não precisam ser marcadas como lidas'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['patch'])
    def marcar_todas_lidas(self, request, room_pk=None):
        """Marca todas as mensagens da sala como lidas"""
        room_id = self.kwargs.get('room_pk')
        sala = get_object_or_404(ChatRoom, id=room_id)
        
        # Verificar permissão usando service
        customer_user = request.user.usuario_user
        if not ChatService.verificar_permissao_sala(sala, customer_user):
            return Response(
                {'error': 'Sem permissão para acessar esta sala'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Usar service para marcar mensagens como lidas
        mensagens_atualizadas = ChatService.marcar_mensagens_como_lidas(sala, customer_user)
        
        return Response(
            {'message': f'{mensagens_atualizadas} mensagens marcadas como lidas'},
            status=status.HTTP_200_OK
        )