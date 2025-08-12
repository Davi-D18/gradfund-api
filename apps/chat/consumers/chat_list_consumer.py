import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from apps.authentication.models import CustomerUser
from apps.chat.models.chat import ChatRoom, Message


class ChatListConsumer(AsyncWebsocketConsumer):
    """Consumer para atualizações da lista de chats"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}'
        
        # Verificar autenticação
        user = await self.get_user()
        if not user:
            await self.close()
            return
        
        # Entrar no grupo do usuário
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Sair do grupo
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    @database_sync_to_async
    def get_user(self):
        """Obter usuário autenticado"""
        try:
            return User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            return None
    
    # Receber mensagem do grupo
    async def chat_list_update(self, event):
        """Enviar atualização da lista de chats"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'room_id': event['room_id'],
            'message_id': event['message_id'],
            'content': event['content'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))