import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class SimpleChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        logger.info(f"Tentativa de conexão WebSocket na sala {self.room_id}")
        
        # Aceitar conexão sem autenticação para teste
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"Conexão WebSocket aceita na sala {self.room_id}")

    async def disconnect(self, close_code):
        logger.info(f"Desconectando da sala {self.room_id}, código: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        logger.info(f"Mensagem recebida: {text_data}")
        
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            # Enviar mensagem de volta para teste
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': 'test_user'
                }
            )
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'timestamp': 'now'
        }))