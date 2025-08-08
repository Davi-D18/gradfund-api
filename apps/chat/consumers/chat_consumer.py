import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from apps.chat.models.chat import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Autenticar usuário via JWT
        user = await self.get_user_from_token()
        if not user:
            await self.close()
            return
            
        self.user = user
        
        # Verificar se usuário tem permissão para acessar a sala
        has_permission = await self.check_room_permission()
        if not has_permission:
            await self.close()
            return
        
        # Entrar no grupo da sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notificar que usuário entrou online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'user'):
            # Notificar que usuário saiu offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'status': 'offline'
                }
            )
        
        # Sair do grupo da sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            await self.handle_message(data)
        elif message_type == 'typing':
            await self.handle_typing(data)

    async def handle_message(self, data):
        content = data.get('content', '').strip()
        if not content:
            return
            
        # Salvar mensagem no banco
        message = await self.save_message(content)
        
        # Enviar mensagem para o grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'content': message.conteudo,
                'user_id': message.remetente.id,
                'username': message.remetente.username,
                'timestamp': message.data_hora.isoformat()
            }
        )

    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        # Enviar status de digitação para outros usuários
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_status',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing
            }
        )

    async def chat_message(self, event):
        # Não enviar mensagem de volta para o remetente
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'message',
                'message_id': event['message_id'],
                'content': event['content'],
                'user_id': event['user_id'],
                'username': event['username'],
                'timestamp': event['timestamp']
            }))

    async def typing_status(self, event):
        # Não enviar status de digitação de volta para o próprio usuário
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    async def user_status(self, event):
        # Não enviar status do próprio usuário
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_status',
                'user_id': event['user_id'],
                'status': event['status']
            }))

    @database_sync_to_async
    def get_user_from_token(self):
        """Autentica usuário via JWT token nos query params"""
        try:
            token = None
            query_string = self.scope.get('query_string', b'').decode()
            
            if 'token=' in query_string:
                token = query_string.split('token=')[1].split('&')[0]
            
            if not token:
                return None
                
            # Validar token JWT
            UntypedToken(token)
            
            # Decodificar token para obter user_id
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            return User.objects.get(id=user_id)
            
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None

    @database_sync_to_async
    def check_room_permission(self):
        """Verifica se usuário tem permissão para acessar a sala"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.participantes.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        """Salva mensagem no banco de dados"""
        room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            sala_chat=room,
            remetente=self.user,
            conteudo=content
        )
        
        # Atualizar timestamp da última mensagem na sala
        room.ultima_mensagem_em = message.data_hora
        room.save()
        
        return message