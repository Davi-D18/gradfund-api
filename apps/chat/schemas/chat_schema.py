from rest_framework import serializers
from django.contrib.auth.models import User
from apps.authentication.models import CustomerUser
from apps.chat.models.chat import ChatRoom, Message


class UserChatSerializer(serializers.ModelSerializer):
    """Serializer básico para usuário no contexto do chat"""
    usuario = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerUser
        fields = ['id', 'usuario']
    
    def get_usuario(self, obj):
        """Retorna dados do usuário Django relacionado"""
        if obj.usuario:
            first_name = obj.usuario.first_name or ''
            last_name = obj.usuario.last_name or ''
            username = obj.usuario.username or ''
            
            # Garantir que sempre tenha um nome para exibir
            display_name = ''
            if first_name and last_name:
                display_name = f"{first_name} {last_name}"
            elif first_name:
                display_name = first_name
            else:
                display_name = username
            
            return {
                'id': obj.usuario.id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'display_name': display_name
            }
        return None


class MessageSerializer(serializers.ModelSerializer):
    """Serializer para mensagens do chat"""
    remetente = UserChatSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'conteudo', 'remetente', 'enviado_em',
            'tipo_mensagem', 'lida', 'entregue_em', 'lida_em'
        ]
        read_only_fields = ['id', 'enviado_em', 'remetente', 'entregue_em', 'lida_em']


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer para salas de chat"""
    participantes = UserChatSerializer(many=True, read_only=True)
    ultima_mensagem = serializers.SerializerMethodField()
    mensagens_nao_lidas = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'participantes', 'servico', 'criado_em', 
            'atualizado_em', 'ativo', 'ultima_mensagem_em',
            'ultima_mensagem', 'mensagens_nao_lidas'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em', 'ultima_mensagem_em']
    
    def get_ultima_mensagem(self, obj):
        """Retorna a última mensagem da sala"""
        ultima = obj.mensagens.order_by('-enviado_em').first()
        if ultima:
            return {
                'id': ultima.id,
                'conteudo': ultima.conteudo,
                'enviado_em': ultima.enviado_em,
                'remetente': {
                    'id': ultima.remetente.id,
                    'usuario': {
                        'id': ultima.remetente.usuario.id,
                        'username': ultima.remetente.usuario.username,
                        'first_name': ultima.remetente.usuario.first_name or '',
                        'last_name': ultima.remetente.usuario.last_name or '',
                        'display_name': (
                            f"{ultima.remetente.usuario.first_name} {ultima.remetente.usuario.last_name}".strip()
                            if ultima.remetente.usuario.first_name or ultima.remetente.usuario.last_name
                            else ultima.remetente.usuario.username
                        )
                    }
                }
            }
        return None
    
    def get_mensagens_nao_lidas(self, obj):
        """Retorna quantidade de mensagens não lidas para o usuário atual"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            current_user = request.user.usuario_user
            return obj.mensagens.filter(
                lida=False
            ).exclude(remetente=current_user).count()
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
            CustomerUser.objects.get(id=value)
            return value
        except CustomerUser.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado")
    
    def create(self, validated_data):
        """Cria sala de chat com os participantes"""
        participante_id = validated_data.pop('participante_id')
        participante = CustomerUser.objects.get(id=participante_id)
        
        # Criar sala
        sala = ChatRoom.objects.create(**validated_data)
        
        # Adicionar participantes
        current_user = self.context['request'].user.usuario_user
        sala.participantes.add(current_user, participante)
        
        return sala