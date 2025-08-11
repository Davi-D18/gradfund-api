from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from apps.chat.models.chat import ChatRoom
from apps.chat.schemas.chat_schema import ChatRoomSerializer, CreateChatRoomSerializer
from apps.chat.services.chat_service import ChatService


class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar salas de chat"""
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas salas onde o usuário é participante"""
        customer_user = self.request.user.usuario_user
        return ChatService.obter_salas_usuario(customer_user).prefetch_related(
            'mensagens__remetente__usuario'
        )
    
    def get_serializer_class(self):
        """Usa serializer específico para criação"""
        if self.action == 'create':
            return CreateChatRoomSerializer
        return ChatRoomSerializer
    
    def create(self, request, *args, **kwargs):
        """Cria nova sala de chat"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Usar service para criar sala
        sala = serializer.save()
        return Response(
            ChatRoomSerializer(sala, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['patch'])
    def desativar(self, request, pk=None):
        """Desativa uma sala de chat"""
        sala = self.get_object()
        
        # Verificar permissão usando service
        customer_user = request.user.usuario_user
        if not ChatService.verificar_permissao_sala(sala, customer_user):
            return Response(
                {'error': 'Sem permissão para desativar esta sala'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        sala.ativo = False
        sala.save()
        
        return Response(
            {'message': 'Sala desativada com sucesso'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def criar_por_servico(self, request):
        """Cria sala de chat baseada em um serviço"""
        servico_id = request.data.get('servico_id')
        
        if not servico_id:
            return Response(
                {'error': 'servico_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar criação
        customer_user = request.user.usuario_user
        validacao = ChatService.validar_criacao_sala(servico_id, customer_user)
        if not validacao['valido']:
            return Response(
                {'error': validacao['erro']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Criar ou obter sala
        try:
            sala = ChatService.criar_ou_obter_sala_por_servico(servico_id, customer_user)
            return Response(
                ChatRoomSerializer(sala, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )