from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


class Command(BaseCommand):
    help = 'Testa notificações de chat'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='ID do usuário para testar')

    def handle(self, *args, **options):
        user_id = options['user_id']
        channel_layer = get_channel_layer()
        
        # Enviar notificação de teste
        async_to_sync(channel_layer.group_send)(
            f'user_{user_id}',
            {
                'type': 'chat_list_update',
                'room_id': 999,
                'message_id': 999,
                'content': 'Mensagem de teste',
                'sender_id': 1,
                'timestamp': '2024-01-01T10:00:00Z'
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Notificação de teste enviada para usuário {user_id}')
        )