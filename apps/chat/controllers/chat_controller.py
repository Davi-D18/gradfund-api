from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from apps.chat.models.chat import ChatRoom
from apps.chat.schemas.chat_schema import ChatRoomSerializer, CreateChatRoomSerializer


class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar salas de chat"""
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas salas onde o usuário é participante"""
        return ChatRoom.objects.filter(
            participantes=self.request.user,
            ativo=True
        ).prefetch_related('participantes', 'message_set').order_by('-ultima_mensagem_em')
    
    def get_serializer_class(self):
        """Usa serializer específico para criação"""
        if self.action == 'create':
            return CreateChatRoomSerializer
        return ChatRoomSerializer
    
    def create(self, request, *args, **kwargs):
        """Cria nova sala de chat"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verificar se já existe sala entre os usuários para o mesmo serviço
        participante_id = serializer.validated_data['participante_id']
        servico = serializer.validated_data.get('servico')
        
        sala_existente = ChatRoom.objects.filter(
            participantes=request.user,
            ativo=True
        ).filter(
            participantes=participante_id
        ).filter(servico=servico).first()
        
        if sala_existente:
            return Response(
                ChatRoomSerializer(sala_existente, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
        
        # Criar nova sala
        sala = serializer.save()
        return Response(
            ChatRoomSerializer(sala, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['patch'])
    def desativar(self, request, pk=None):
        """Desativa uma sala de chat"""
        sala = self.get_object()
        sala.ativo = False
        sala.save()
        
        return Response(
            {'message': 'Sala desativada com sucesso'},
            status=status.HTTP_200_OK
        )