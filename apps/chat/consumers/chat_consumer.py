import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.authentication.models import CustomerUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from ..models import ChatRoom, Message

logger = logging.getLogger(__name__)

# Dicionário para controlar conexões ativas por usuário/sala
# Estrutura: {"user_X_room_Y": {"channel": "channel_name", "user_id": X, "username": "nome"}}
active_connections = {}

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garantir que cada instância tenha suas próprias variáveis
        self.user = None
        self.user_id = None
        self.room_id = None
        self.room_group_name = None
        self.connection_key = None
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        logger.info(f"🔗 NOVA CONEXÃO WebSocket na sala {self.room_id}")
        
        # Usar usuário do middleware JWT
        self.user = self.scope.get('user')
        if not self.user or not isinstance(self.user, CustomerUser):
            logger.error("Conexão rejeitada: usuário não autenticado")
            await self.close(code=4001)  # Unauthorized
            return
        
        self.user_id = self.user.id
        logger.info(f"🔍 CONNECT - CustomerUser autenticado (ID: {self.user_id})")
        
        # Chave única para usuário/sala
        connection_key = f"user_{self.user.id}_room_{self.room_id}"
        
        # Fechar conexão anterior se existir (com delay para evitar conflitos)
        if connection_key in active_connections:
            old_connection = active_connections[connection_key]
            old_channel = old_connection['channel'] if isinstance(old_connection, dict) else old_connection
            # Só fechar se for realmente uma conexão diferente
            if old_channel != self.channel_name:
                logger.info(f"⚠️ Fechando conexão anterior do CustomerUser ID {self.user.id}")
                await self.channel_layer.send(old_channel, {
                    'type': 'disconnect_duplicate'
                })
                # Pequeno delay para evitar conflitos
                import asyncio
                await asyncio.sleep(0.1)
        
        # Registrar nova conexão com detalhes do usuário
        active_connections[connection_key] = {
            'channel': self.channel_name,
            'user_id': self.user.id,
            'username': f'CustomerUser_{self.user.id}',
            'room_id': self.room_id
        }
        self.connection_key = connection_key
        
        logger.info(f"✅ CustomerUser ID {self.user.id} conectado na sala {self.room_id}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Marcar mensagens antigas como lidas
        await self.mark_old_messages_as_read()

    async def disconnect(self, close_code):
        logger.info(f"🔌 DESCONEXÃO WebSocket - Channel: {self.channel_name}")
        if hasattr(self, 'user') and self.user and isinstance(self.user, CustomerUser):
            logger.info(f"   - CustomerUser ID: {self.user.id}")
        
        # Remover da lista de conexões ativas
        if hasattr(self, 'connection_key') and self.connection_key and self.connection_key in active_connections:
            connection_data = active_connections[self.connection_key]
            current_channel = connection_data['channel'] if isinstance(connection_data, dict) else connection_data
            if current_channel == self.channel_name:
                del active_connections[self.connection_key]
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def disconnect_duplicate(self, event):
        """Método para fechar conexões duplicadas"""
        logger.info(f"🔄 Fechando conexão duplicada: {self.channel_name}")
        await self.close(code=4000)  # Código personalizado para duplicata

    async def receive(self, text_data):
        logger.info(f"=== MÉTODO RECEIVE CHAMADO ===")
        logger.info(f"Dados recebidos: {text_data}")
        logger.info(f"Tipo dos dados: {type(text_data)}")
        try:
            text_data_json = json.loads(text_data)
            logger.info(f"JSON parseado: {text_data_json}")
            
            message = text_data_json.get('message', '')
            message_type = text_data_json.get('type', 'message')
            
            logger.info(f"Campos extraídos - message: '{message}', type: '{message_type}'")
            
            # Ignorar mensagens de typing
            if message_type == 'typing':
                logger.info("Mensagem de typing ignorada")
                return
            
            # Tratar evento de mensagem lida
            if message_type == 'message_read':
                message_id = text_data_json.get('message_id')
                if message_id:
                    await self.mark_message_as_read(message_id)
                return
            
            # Validar mensagem obrigatória
            if not message:
                logger.error(f"Mensagem vazia: '{message}'")
                await self.send(text_data=json.dumps({
                    'error': 'Mensagem é obrigatória'
                }))
                return
            
            # Usar usuário já autenticado pelo middleware
            if not self.user or not isinstance(self.user, CustomerUser):
                logger.error("❌ RECEIVE - Usuário não autenticado")
                await self.send(text_data=json.dumps({
                    'error': 'Não autenticado'
                }))
                return
            
            user_id = self.user.id
            logger.info(f"📨 Mensagem de CustomerUser ID {user_id}: {message}")
            


            # Save message to database
            saved_message = await self.save_message(user_id, message)
            logger.info(f"Retorno do save_message: {saved_message}")
            if saved_message:
                logger.info(f"✅ Mensagem salva com sucesso: ID {saved_message.id}")
            else:
                logger.error("❌ Falha ao salvar mensagem no banco - saved_message é None")

            # Send message to room group
            message_id = saved_message.id if saved_message else None
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': user_id,
                    'username': f'CustomerUser_{self.user.id}',
                    'message_id': message_id
                }
            )
            
            # Notificar globalmente sobre nova mensagem para atualizar lista de chats
            if saved_message:
                logger.info(f"🔔 Iniciando notificação global para mensagem {saved_message.id}")
                await self.notify_chat_list_update(saved_message)
            else:
                logger.error(f"❌ Não foi possível notificar - mensagem não foi salva")
        except json.JSONDecodeError as e:
            logger.error(f"JSON inválido: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'JSON inválido'
            }))
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Erro ao processar mensagem'
            }))

    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        username = event.get('username', '')
        message_id = event.get('message_id')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'username': username,
            'message_id': message_id,
            'type': 'message'
        }))
        
        # Auto-marcar como lida se não for o remetente
        if message_id and user_id != self.user.id:
            await self.auto_mark_as_read(message_id)



    async def mark_message_as_read(self, message_id):
        """Marca mensagem como lida e notifica outros usuários"""
        success = await self.mark_message_read_db(message_id)
        if success:
            # Notificar outros usuários na sala
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_read_event',
                    'message_id': message_id,
                    'read_by_user_id': self.user.id
                }
            )
    
    async def message_read_event(self, event):
        """Envia evento de mensagem lida para o WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'read_by_user_id': event['read_by_user_id']
        }))
    
    async def auto_mark_as_read(self, message_id):
        """Marca mensagem automaticamente como lida quando entregue"""
        success = await self.mark_message_read_db(message_id)
        if success:
            # Notificar que foi marcada como lida
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_read_event',
                    'message_id': message_id,
                    'read_by_user_id': self.user.id
                }
            )
    
    @database_sync_to_async
    def mark_message_read_db(self, message_id):
        """Marca mensagem como lida no banco de dados"""
        try:
            message = Message.objects.get(id=message_id, sala_chat_id=self.room_id)
            # Só marcar como lida se não for o remetente
            if message.remetente.id != self.user.id and not message.lida:
                message.lida = True
                message.save()
                logger.info(f"✅ Mensagem {message_id} marcada como lida automaticamente")
                return True
            return False
        except Message.DoesNotExist:
            logger.error(f"❌ Mensagem {message_id} não encontrada")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao marcar mensagem como lida: {str(e)}")
            return False

    async def mark_old_messages_as_read(self):
        """Marca mensagens antigas como lidas quando usuário se conecta"""
        marked_messages = await self.mark_old_messages_db()
        
        # Notificar sobre mensagens marcadas como lidas
        for message_id in marked_messages:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_read_event',
                    'message_id': message_id,
                    'read_by_user_id': self.user.id
                }
            )
    
    @database_sync_to_async
    def mark_old_messages_db(self):
        """Marca mensagens antigas como lidas no banco"""
        try:
            # Buscar mensagens não lidas de outros usuários
            unread_messages = Message.objects.filter(
                sala_chat_id=self.room_id,
                lida=False
            ).exclude(remetente=self.user)
            
            marked_ids = list(unread_messages.values_list('id', flat=True))
            
            # Marcar como lidas
            unread_messages.update(lida=True)
            
            logger.info(f"✅ Marcadas {len(marked_ids)} mensagens antigas como lidas para CustomerUser {self.user.id}")
            return marked_ids
            
        except Exception as e:
            logger.error(f"❌ Erro ao marcar mensagens antigas: {str(e)}")
            return []

    async def notify_chat_list_update(self, message_obj):
        """Notifica participantes sobre nova mensagem para atualizar lista de chats"""
        participants = await self.get_chat_participants()
        logger.info(f"🔔 Notificando {len(participants)} participantes sobre nova mensagem na sala {self.room_id}")
        
        for participant in participants:
            logger.info(f"📤 Enviando notificação para usuário {participant.id} no grupo user_{participant.id}")
            # Enviar para canal pessoal de cada participante
            await self.channel_layer.group_send(
                f'user_{participant.id}',
                {
                    'type': 'chat_list_update',
                    'room_id': self.room_id,
                    'message': {
                        'id': message_obj.id,
                        'conteudo': message_obj.conteudo,
                        'enviado_em': message_obj.enviado_em.isoformat(),
                        'remetente': {
                            'id': message_obj.remetente.id,
                            'username': message_obj.remetente.usuario.username
                        }
                    }
                }
            )
    
    @database_sync_to_async
    def get_chat_participants(self):
        """Obtém participantes do chat"""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            return list(chat_room.participantes.all())
        except ChatRoom.DoesNotExist:
            return []

    @database_sync_to_async
    def save_message(self, user_id, message):
        try:
            # Buscar diretamente o CustomerUser pelo ID
            customer_user = CustomerUser.objects.get(id=user_id)
            chat_room = ChatRoom.objects.get(id=self.room_id)
            
            message_obj = Message.objects.create(
                sala_chat=chat_room,
                remetente=customer_user,
                conteudo=message
            )
            
            logger.info(f"✅ Mensagem salva: ID {message_obj.id}, Remetente: {customer_user.usuario.username} (CustomerUser ID: {customer_user.id})")
            return message_obj
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar mensagem: {str(e)}")
            return None