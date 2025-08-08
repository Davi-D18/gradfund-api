from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Command(BaseCommand):
    help = 'Testa a configuração do Django Channels e Redis'

    def handle(self, *args, **options):
        try:
            channel_layer = get_channel_layer()
            
            if channel_layer is None:
                self.stdout.write(
                    self.style.ERROR('ERRO Channel layer nao configurado')
                )
                return
            
            # Teste básico de envio/recebimento
            async_to_sync(channel_layer.send)(
                'test-channel', 
                {'type': 'test.message', 'text': 'Hello World'}
            )
            
            self.stdout.write(
                self.style.SUCCESS('OK Django Channels configurado com sucesso!')
            )
            self.stdout.write(f'Backend: {channel_layer.__class__.__name__}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'ERRO na configuracao: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('Certifique-se de que o Redis esta rodando')
            )