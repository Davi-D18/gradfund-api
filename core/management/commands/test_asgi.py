from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Verifica configuração ASGI'

    def handle(self, *args, **options):
        self.stdout.write("=== Verificação ASGI ===")
        
        # Verificar ASGI_APPLICATION
        asgi_app = getattr(settings, 'ASGI_APPLICATION', None)
        if asgi_app:
            self.stdout.write(self.style.SUCCESS(f"OK ASGI_APPLICATION: {asgi_app}"))
        else:
            self.stdout.write(self.style.ERROR("ERRO ASGI_APPLICATION nao configurado"))
        
        # Verificar Channels
        if 'channels' in settings.INSTALLED_APPS:
            self.stdout.write(self.style.SUCCESS("OK Django Channels instalado"))
        else:
            self.stdout.write(self.style.ERROR("ERRO Django Channels nao encontrado"))
        
        # Verificar Channel Layers
        channel_layers = getattr(settings, 'CHANNEL_LAYERS', None)
        if channel_layers:
            backend = channel_layers['default']['BACKEND']
            self.stdout.write(self.style.SUCCESS(f"OK Channel Layer: {backend}"))
        else:
            self.stdout.write(self.style.ERROR("ERRO CHANNEL_LAYERS nao configurado"))
        
        # Testar import do routing
        try:
            from apps.chat.routing import websocket_urlpatterns
            self.stdout.write(self.style.SUCCESS(f"OK WebSocket URLs: {len(websocket_urlpatterns)} rotas"))
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"ERRO no routing: {e}"))
        
        # Testar import do consumer
        try:
            from apps.chat.consumers import ChatConsumer
            self.stdout.write(self.style.SUCCESS("OK ChatConsumer importado"))
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"ERRO no consumer: {e}"))
        
        self.stdout.write("\n=== Como rodar o servidor ===")
        self.stdout.write("python manage.py runserver")
        self.stdout.write("(Django 3.0+ usa ASGI automaticamente)")
        
        self.stdout.write("\n=== Endpoint WebSocket ===")
        self.stdout.write("ws://localhost:8000/ws/chat/1/?token=SEU_TOKEN")