#!/usr/bin/env python3
import os
import sys
import django
import asyncio

# Configurar Django
sys.path.append('/home/ld/Documentos/projetos/Senai/Back-end/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.chat.models import ChatRoom, Message
from apps.chat.consumers.chat_consumer import ChatConsumer

async def test_save_message():
    print("=== Teste do método save_message ===")
    
    # Obter dados de teste
    user = User.objects.first()
    chat_room = ChatRoom.objects.first()
    
    if not user or not chat_room:
        print("Erro: Usuário ou sala de chat não encontrados")
        return
    
    print(f"Usuário: {user.username} (ID: {user.id})")
    print(f"Sala: {chat_room.id}")
    print(f"Mensagens antes: {Message.objects.count()}")
    
    # Simular o consumer
    consumer = ChatConsumer()
    consumer.room_id = str(chat_room.id)
    
    # Testar o método save_message (versão assíncrona)
    try:
        result = await consumer.save_message(user.id, "Teste do método save_message")
        print(f"Resultado: {result}")
        print(f"Mensagens depois: {Message.objects.count()}")
        
        if result:
            print(f"✅ Mensagem salva com sucesso! ID: {result.id}")
        else:
            print("❌ Falha ao salvar mensagem")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_save_message())