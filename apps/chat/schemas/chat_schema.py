from rest_framework import serializers
from django.contrib.auth.models import User
from apps.chat.models.chat import ChatRoom, Message


class UserChatSerializer(serializers.ModelSerializer):
    """Serializer básico para usuário no contexto do chat"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer para mensagens do chat"""
    remetente = UserChatSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'conteudo', 'remetente', 'data_hora',
            'tipo_mensagem', 'lida', 'entregue_em', 'lida_em'
        ]
        read_only_fields = ['id', 'data_hora', 'remetente', 'entregue_em', 'lida_em']


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer para salas de chat"""
    participantes = UserChatSerializer(many=True, read_only=True)
    ultima_mensagem = serializers.SerializerMethodField()
    total_mensagens = serializers.SerializerMethodField()
    mensagens_nao_lidas = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'participantes', 'servico', 'criado_em', 
            'atualizado_em', 'ativo', 'ultima_mensagem_em',
            'ultima_mensagem', 'total_mensagens', 'mensagens_nao_lidas'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em', 'ultima_mensagem_em']
    
    def get_ultima_mensagem(self, obj):
        """Retorna a última mensagem da sala"""
        ultima = obj.message_set.order_by('-data_hora').first()
        if ultima:
            return MessageSerializer(ultima).data
        return None
    
    def get_total_mensagens(self, obj):
        """Retorna total de mensagens na sala"""
        return obj.message_set.count()
    
    def get_mensagens_nao_lidas(self, obj):
        """Retorna mensagens não lidas pelo usuário atual"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.chat.services.chat_service import ChatService
            return ChatService.contar_mensagens_nao_lidas(obj, request.user)
        return 0


class CreateChatRoomSerializer(serializers.ModelSerializer):
    """Serializer para criação de salas de chat"""
    participante_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ChatRoom
        fields = ['servico', 'participante_id']
    
    def validate_participante_id(self, value):
        """Valida se o participante existe"""
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado")
    
    def create(self, validated_data):
        """Cria sala de chat com os participantes"""
        participante_id = validated_data.pop('participante_id')
        participante = User.objects.get(id=participante_id)
        
        # Criar sala
        sala = ChatRoom.objects.create(**validated_data)
        
        # Adicionar participantes
        sala.participantes.add(self.context['request'].user, participante)
        
        return sala