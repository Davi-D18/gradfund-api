#!/usr/bin/env python3
"""
Script para testar salvamento direto de mensagens
"""
import os
import django
import sys

# Configurar Django
sys.path.append('/home/ld/Documentos/projetos/Senai/Back-end/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.chat.models import ChatRoom, Message
from django.contrib.auth.models import User

def test_direct_message_save():
    """Testa salvamento direto de mensagens"""
    print("💾 TESTE DE SALVAMENTO DIRETO DE MENSAGENS\n")
    
    # Buscar dados
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
    
    # Teste 1: Salvar mensagem do usuário 2
    print("📝 TESTE 1: Salvando mensagem do usuário 2")
    
    try:
        message_user_2 = Message.objects.create(
            sala_chat=chat_room,
            remetente=user_2,
            conteudo="Teste direto usuário 2"
        )
        
        # Verificar o que foi salvo
        message_user_2.refresh_from_db()
        print(f"✅ Mensagem criada:")
        print(f"   - ID: {message_user_2.id}")
        print(f"   - Remetente: {message_user_2.remetente.username} (ID: {message_user_2.remetente.id})")
        print(f"   - Conteúdo: '{message_user_2.conteudo}'")
        
        if message_user_2.remetente.id == 2:
            print("✅ CORRETO: Mensagem salva com remetente ID 2")
        else:
            print(f"❌ ERRO: Mensagem salva com remetente ID {message_user_2.remetente.id}")
            
    except Exception as e:
        print(f"❌ Erro ao salvar mensagem do usuário 2: {e}")
    
    print("\n" + "-"*40)
    
    # Teste 2: Salvar mensagem do usuário 3
    print("📝 TESTE 2: Salvando mensagem do usuário 3")
    
    try:
        message_user_3 = Message.objects.create(
            sala_chat=chat_room,
            remetente=user_3,
            conteudo="Teste direto usuário 3"
        )
        
        # Verificar o que foi salvo
        message_user_3.refresh_from_db()
        print(f"✅ Mensagem criada:")
        print(f"   - ID: {message_user_3.id}")
        print(f"   - Remetente: {message_user_3.remetente.username} (ID: {message_user_3.remetente.id})")
        print(f"   - Conteúdo: '{message_user_3.conteudo}'")
        
        if message_user_3.remetente.id == 3:
            print("✅ CORRETO: Mensagem salva com remetente ID 3")
        else:
            print(f"❌ ERRO: Mensagem salva com remetente ID {message_user_3.remetente.id}")
            
    except Exception as e:
        print(f"❌ Erro ao salvar mensagem do usuário 3: {e}")
    
    print("\n" + "="*60)
    
    # Verificar todas as mensagens na sala
    print("📋 TODAS AS MENSAGENS NA SALA:")
    all_messages = Message.objects.filter(sala_chat=chat_room).order_by('-enviado_em')
    
    for msg in all_messages:
        print(f"   - ID: {msg.id}, Remetente: {msg.remetente.username} (ID: {msg.remetente.id}), Conteúdo: '{msg.conteudo[:30]}...'")
    
    print(f"\nTotal de mensagens: {all_messages.count()}")
    
    # Contar por remetente
    remetente_counts = {}
    for msg in all_messages:
        remetente_id = msg.remetente.id
        if remetente_id not in remetente_counts:
            remetente_counts[remetente_id] = 0
        remetente_counts[remetente_id] += 1
    
    print("\n📊 Distribuição por remetente:")
    for remetente_id, count in remetente_counts.items():
        try:
            user = User.objects.get(id=remetente_id)
            print(f"   - Usuário {remetente_id} ({user.username}): {count} mensagens")
        except User.DoesNotExist:
            print(f"   - Usuário {remetente_id} (DELETADO): {count} mensagens")

if __name__ == "__main__":
    test_direct_message_save()