#!/usr/bin/env python3
"""
Script para debugar o problema da API de mensagens
"""
import os
import django
import sys

# Configurar Django
sys.path.append('/home/ld/Documentos/projetos/Senai/Back-end/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.chat.models import ChatRoom, Message
from apps.chat.schemas.chat_schema import MessageSerializer
from django.contrib.auth.models import User

def debug_message_api():
    """Debug da API de mensagens"""
    print("🔍 DEBUG DA API DE MENSAGENS\n")
    
    # Buscar sala e usuários
    try:
        chat_room = ChatRoom.objects.get(id=1)
        user_2 = User.objects.get(id=2)
        user_3 = User.objects.get(id=3)
        print(f"💬 Sala: {chat_room}")
        print(f"👤 Usuário 2: {user_2.username}")
        print(f"👤 Usuário 3: {user_3.username}")
    except Exception as e:
        print(f"❌ Erro ao buscar dados: {e}")
        return
    
    print("\n" + "="*60)
    
    # Consulta direta no banco
    print("🗃️ CONSULTA DIRETA NO BANCO:")
    messages = Message.objects.filter(sala_chat=chat_room).order_by('-enviado_em')
    
    for msg in messages:
        print(f"   - ID: {msg.id}")
        print(f"     Remetente: {msg.remetente.username} (ID: {msg.remetente.id})")
        print(f"     Conteúdo: '{msg.conteudo[:30]}...'")
        print(f"     Enviado em: {msg.enviado_em}")
        print()
    
    print("="*60)
    
    # Testar serializer
    print("📄 TESTE DO SERIALIZER:")
    serializer = MessageSerializer(messages, many=True)
    serialized_data = serializer.data
    
    for msg_data in serialized_data:
        print(f"   - ID: {msg_data['id']}")
        print(f"     Remetente ID: {msg_data['remetente']['id']}")
        print(f"     Remetente Username: {msg_data['remetente']['username']}")
        print(f"     Conteúdo: '{msg_data['conteudo'][:30]}...'")
        print()
    
    print("="*60)
    
    # Verificar se há inconsistência
    print("🔍 VERIFICAÇÃO DE INCONSISTÊNCIA:")
    for i, msg in enumerate(messages):
        serialized_msg = serialized_data[i]
        
        db_remetente_id = msg.remetente.id
        serialized_remetente_id = serialized_msg['remetente']['id']
        
        if db_remetente_id != serialized_remetente_id:
            print(f"❌ INCONSISTÊNCIA na mensagem ID {msg.id}:")
            print(f"   Banco: remetente_id = {db_remetente_id}")
            print(f"   Serializer: remetente_id = {serialized_remetente_id}")
        else:
            print(f"✅ Mensagem ID {msg.id}: Consistente (remetente_id = {db_remetente_id})")
    
    print("\n" + "="*60)
    
    # Simular requisição da API
    print("🌐 SIMULAÇÃO DA API REST:")
    print("Simulando GET /api/v1/chat/rooms/1/messages/")
    
    # Filtrar como a API faz
    api_messages = Message.objects.filter(
        sala_chat=chat_room
    ).select_related('remetente').order_by('-enviado_em')
    
    print(f"Total de mensagens retornadas: {api_messages.count()}")
    
    for msg in api_messages:
        print(f"   - Mensagem ID {msg.id}: remetente_id = {msg.remetente.id} ({msg.remetente.username})")

if __name__ == "__main__":
    debug_message_api()