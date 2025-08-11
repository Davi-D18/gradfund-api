import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class UserConsumer(AsyncWebsocketConsumer):
    """Consumer para notificações globais do usuário"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}'
        
        # Usar usuário do middleware JWT
        self.user = self.scope.get('user')
        if not self.user or str(self.user.id) != str(self.user_id):
            logger.error("Conexão rejeitada: usuário não autorizado")
            await self.close(code=4001)
            return
        
        # Join user group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"✅ Usuário {self.user_id} conectado ao WebSocket global no grupo {self.user_group_name}")

    async def disconnect(self, close_code):
        # Leave user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        logger.info(f"🔌 Usuário {self.user_id} desconectado do WebSocket global do grupo {self.user_group_name}")

    async def chat_list_update(self, event):
        """Envia atualização da lista de chats"""
        logger.info(f"📨 UserConsumer enviando chat_list_update para usuário {self.user_id}")
        await self.send(text_data=json.dumps({
            'type': 'chat_list_update',
            'room_id': event['room_id'],
            'message': event['message']
        }))
        logger.info(f"✅ chat_list_update enviado com sucesso para usuário {self.user_id}")