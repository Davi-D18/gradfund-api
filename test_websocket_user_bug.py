#!/usr/bin/env python3
"""
Script para reproduzir o bug de usuário incorreto no WebSocket
"""
import os
import django
import sys

# Configurar Django
sys.path.append('/home/ld/Documentos/projetos/Senai/Back-end/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from apps.chat.models import ChatRoom, Message
from apps.chat.consumers.chat_consumer import active_connections

def test_websocket_user_bug():
    """Testa o bug de usuário incorreto no WebSocket"""
    print("🐛 TESTE DO BUG DE USUÁRIO INCORRETO NO WEBSOCKET\n")
    
    # Limpar conexões ativas
    active_connections.clear()
    print("🧹 Conexões ativas limpas")
    
    # Buscar usuários
    try:
        user_2 = User.objects.get(id=2)  # Clara
        user_3 = User.objects.get(id=3)  # Clara Tonha
        print(f"👤 Usuário 2: {user_2.username}")
        print(f"👤 Usuário 3: {user_3.username}")
    except User.DoesNotExist as e:
        print(f"❌ Usuário não encontrado: {e}")
        return
    
    # Buscar sala de chat
    try:
        chat_room = ChatRoom.objects.get(id=1)
        print(f"💬 Sala de chat: {chat_room}")
    except ChatRoom.DoesNotExist:
        print("❌ Sala de chat ID 1 não encontrada")
        return
    
    print("\n" + "="*60)
    
    # Simular tokens para ambos usuários
    token_user_2 = str(AccessToken.for_user(user_2))
    token_user_3 = str(AccessToken.for_user(user_3))
    
    print(f"🔑 Token usuário 2: {token_user_2[:50]}...")
    print(f"🔑 Token usuário 3: {token_user_3[:50]}...")
    
    # Verificar mensagens existentes na sala
    messages = Message.objects.filter(sala_chat=chat_room).order_by('-enviado_em')[:5]
    print(f"\n📨 Últimas 5 mensagens na sala:")
    for msg in messages:
        print(f"   - ID: {msg.id}, Remetente: {msg.remetente.username} (ID: {msg.remetente.id}), Conteúdo: '{msg.conteudo[:30]}...'")
    
    # Verificar se há padrão no problema
    all_messages = Message.objects.filter(sala_chat=chat_room)
    remetente_counts = {}
    for msg in all_messages:
        remetente_id = msg.remetente.id
        if remetente_id not in remetente_counts:
            remetente_counts[remetente_id] = 0
        remetente_counts[remetente_id] += 1
    
    print(f"\n📊 Total de mensagens na sala: {all_messages.count()}")
    
    print(f"\n📊 Distribuição de mensagens por remetente:")
    for remetente_id, count in remetente_counts.items():
        try:
            user = User.objects.get(id=remetente_id)
            print(f"   - Usuário {remetente_id} ({user.username}): {count} mensagens")
        except User.DoesNotExist:
            print(f"   - Usuário {remetente_id} (DELETADO): {count} mensagens")
    
    print("\n" + "="*60)
    print("🔍 ANÁLISE DO PROBLEMA:")
    
    if 3 in remetente_counts and 2 not in remetente_counts:
        print("❌ PROBLEMA CONFIRMADO: Todas as mensagens estão sendo salvas como usuário ID 3")
        print("   Isso indica que o WebSocket Consumer está usando um usuário fixo/cached")
        print(f"   Usuário ID 3 tem {remetente_counts[3]} mensagens")
    elif 3 in remetente_counts and 2 in remetente_counts:
        print("✅ PROBLEMA PARCIAL: Ambos usuários têm mensagens, mas pode haver inconsistência")
        print(f"   Usuário ID 2 tem {remetente_counts.get(2, 0)} mensagens")
        print(f"   Usuário ID 3 tem {remetente_counts.get(3, 0)} mensagens")
    elif 2 in remetente_counts and 3 not in remetente_counts:
        print("🔄 SITUAÇÃO INVERSA: Todas as mensagens são do usuário ID 2")
        print(f"   Usuário ID 2 tem {remetente_counts[2]} mensagens")
    else:
        print("🤔 SITUAÇÃO INESPERADA: Padrão de mensagens não corresponde ao relatado")
        print(f"   Remetentes encontrados: {list(remetente_counts.keys())}")
    
    print("\n💡 POSSÍVEIS CAUSAS:")
    print("   1. Cache de usuário no WebSocket Consumer")
    print("   2. Token sendo decodificado incorretamente")
    print("   3. Variável de instância sendo compartilhada entre conexões")
    print("   4. Problema no middleware de autenticação")
    print("   5. Frontend enviando token errado")
    print("   6. Múltiplas conexões causando confusão de estado")
    
    print(f"\n🔧 CONEXÕES ATIVAS ATUAIS: {len(active_connections)}")
    for key, data in active_connections.items():
        if isinstance(data, dict):
            print(f"   - {key}: Usuário {data.get('user_id')} ({data.get('username')})")
        else:
            print(f"   - {key}: {data}")

if __name__ == "__main__":
    test_websocket_user_bug()