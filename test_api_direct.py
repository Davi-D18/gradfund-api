#!/usr/bin/env python3
import os
import django
import sys

sys.path.append('/home/ld/Documentos/projetos/Senai/Back-end/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.chat.models import Message, ChatRoom
from apps.chat.schemas.chat_schema import MessageSerializer

def test_api_direct():
    print("🔍 TESTE DIRETO DA API\n")
    
    # Buscar mensagens mais recentes
    messages = Message.objects.filter(sala_chat_id=1).order_by('-enviado_em')[:3]
    
    print("📋 MENSAGENS NO BANCO:")
    for msg in messages:
        print(f"ID: {msg.id}, Remetente: {msg.remetente.username} (ID: {msg.remetente.id})")
    
    print("\n📄 SERIALIZER OUTPUT:")
    serializer = MessageSerializer(messages, many=True)
    for msg_data in serializer.data:
        print(f"ID: {msg_data['id']}, Remetente ID: {msg_data['remetente']['id']}")

if __name__ == "__main__":
    test_api_direct()