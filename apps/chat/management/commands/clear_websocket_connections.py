from django.core.management.base import BaseCommand
from apps.chat.consumers.chat_consumer import active_connections


class Command(BaseCommand):
    help = 'Limpa todas as conexões WebSocket ativas'

    def handle(self, *args, **options):
        count = len(active_connections)
        active_connections.clear()
        self.stdout.write(
            self.style.SUCCESS(f'✅ {count} conexões WebSocket limpas com sucesso')
        )