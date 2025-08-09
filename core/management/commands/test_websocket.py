import asyncio
import websockets
import json
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Testa conexão WebSocket do chat'

    def add_arguments(self, parser):
        parser.add_argument('--room', type=int, default=1, help='ID da sala de chat')
        parser.add_argument('--token', type=str, help='Token JWT para autenticação')

    def handle(self, *args, **options):
        room_id = options['room']
        token = options.get('token', 'test-token')
        
        async def test_websocket():
            uri = f"ws://localhost:8000/ws/chat/{room_id}/?token={token}"
            
            try:
                self.stdout.write(f"Conectando em: {uri}")
                
                async with websockets.connect(uri) as websocket:
                    self.stdout.write(self.style.SUCCESS("Conexão WebSocket estabelecida!"))
                    
                    # Enviar mensagem de teste
                    test_message = {
                        "message": "Mensagem de teste",
                        "user_id": 1
                    }
                    
                    await websocket.send(json.dumps(test_message))
                    self.stdout.write("Mensagem enviada")
                    
                    # Aguardar resposta
                    response = await websocket.recv()
                    self.stdout.write(f"Resposta recebida: {response}")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erro na conexão WebSocket: {str(e)}")
                )
        
        # Executar teste
        asyncio.run(test_websocket())