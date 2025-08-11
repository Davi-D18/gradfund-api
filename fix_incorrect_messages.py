#!/usr/bin/env python3
"""
Script para limpar mensagens incorretas e testar a correção
"""
import os
import django
import sys

# Configurar Django
sys.path.append('/home/ld/Documentos/projetos/Senai/Back-end/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.chat.models import ChatRoom, Message
from apps.chat.consumers.chat_consumer import active_connections

def fix_incorrect_messages():
    """Limpa mensagens incorretas para testar a correção"""
    print("🔧 LIMPEZA DE MENSAGENS INCORRETAS\n")
    
    # Limpar conexões ativas
    active_connections.clear()
    print("🧹 Conexões ativas limpas")
    
    # Buscar sala de chat
    try:
        chat_room = ChatRoom.objects.get(id=1)
        print(f"💬 Sala de chat: {chat_room}")
    except ChatRoom.DoesNotExist:
        print("❌ Sala de chat ID 1 não encontrada")
        return
    
    # Contar mensagens antes
    messages_before = Message.objects.filter(sala_chat=chat_room).count()
    print(f"📊 Mensagens antes da limpeza: {messages_before}")
    
    # Opção 1: Deletar todas as mensagens para teste limpo
    print("\n🗑️ DELETANDO TODAS AS MENSAGENS PARA TESTE LIMPO...")
    deleted_count = Message.objects.filter(sala_chat=chat_room).delete()[0]
    print(f"✅ {deleted_count} mensagens deletadas")
    
    # Verificar se limpeza foi bem-sucedida
    messages_after = Message.objects.filter(sala_chat=chat_room).count()
    print(f"📊 Mensagens após limpeza: {messages_after}")
    
    if messages_after == 0:
        print("✅ LIMPEZA CONCLUÍDA - Sala pronta para teste")
        print("\n📝 PRÓXIMOS PASSOS:")
        print("1. Reiniciar o servidor Django")
        print("2. Conectar com usuário ID 2 no frontend")
        print("3. Enviar mensagem de teste")
        print("4. Verificar se a mensagem é salva com remetente correto")
    else:
        print("❌ ERRO na limpeza - Ainda há mensagens na sala")

if __name__ == "__main__":
    fix_incorrect_messages()