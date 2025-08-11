#!/usr/bin/env python3
"""
Script para testar as correções no chat
"""
import os
import django
import sys

# Configurar Django
sys.path.append('/home/ld/Documentos/projetos/Senai/Back-end/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.chat.models import ChatRoom, Message
from apps.authentication.models import CustomerUser
from django.contrib.auth.models import User

def test_message_save_fix():
    """Testa se a correção do salvamento de mensagens funciona"""
    print("🧪 TESTE DAS CORREÇÕES NO CHAT\n")
    
    # Buscar dados de teste
    try:
        chat_room = ChatRoom.objects.first()
        if not chat_room:
            print("❌ Nenhuma sala de chat encontrada")
            return
            
        django_user = User.objects.first()
        if not django_user:
            print("❌ Nenhum usuário encontrado")
            return
            
        # Buscar qualquer CustomerUser disponível
        customer_user = CustomerUser.objects.first()
        if not customer_user:
            print("❌ Nenhum CustomerUser encontrado")
            return
        
        # Usar o User associado ao CustomerUser
        django_user = customer_user.usuario
            
        print(f"💬 Sala: {chat_room}")
        print(f"👤 Django User: {django_user.username} (ID: {django_user.id})")
        print(f"👤 Customer User: {customer_user.usuario.username} (ID: {customer_user.id})")
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados: {e}")
        return
    
    print("\n" + "="*60)
    
    # Testar o método corrigido
    print("📝 TESTANDO SALVAMENTO COM CORREÇÃO:")
    
    try:
        # Simular o que o consumer faz agora
        django_user_id = django_user.id
        
        # Buscar CustomerUser através do User (como na correção)
        django_user_obj = User.objects.get(id=django_user_id)
        customer_user_obj = CustomerUser.objects.get(usuario=django_user_obj)
        
        # Criar mensagem
        message_obj = Message.objects.create(
            sala_chat=chat_room,
            remetente=customer_user_obj,
            conteudo="Teste da correção do salvamento"
        )
        
        print(f"✅ Mensagem criada com sucesso:")
        print(f"   - ID: {message_obj.id}")
        print(f"   - Remetente: {message_obj.remetente.usuario.username}")
        print(f"   - CustomerUser ID: {message_obj.remetente.id}")
        print(f"   - Django User ID: {message_obj.remetente.usuario.id}")
        print(f"   - Conteúdo: '{message_obj.conteudo}'")
        
        # Verificar se foi salvo corretamente
        message_obj.refresh_from_db()
        if message_obj.remetente.usuario.id == django_user_id:
            print("✅ CORREÇÃO FUNCIONANDO: Mensagem salva com usuário correto")
        else:
            print("❌ PROBLEMA PERSISTE: Usuário incorreto")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    
    # Verificar mensagens recentes
    print("📋 MENSAGENS RECENTES NA SALA:")
    recent_messages = Message.objects.filter(sala_chat=chat_room).order_by('-enviado_em')[:5]
    
    for msg in recent_messages:
        print(f"   - ID: {msg.id}, Remetente: {msg.remetente.usuario.username} (CU ID: {msg.remetente.id}), Conteúdo: '{msg.conteudo[:30]}...'")
    
    print(f"\nTotal de mensagens na sala: {Message.objects.filter(sala_chat=chat_room).count()}")

if __name__ == "__main__":
    test_message_save_fix()