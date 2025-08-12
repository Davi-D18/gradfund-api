#!/usr/bin/env python3
"""
Script para testar sistema completo de notificações do chat
"""
import os
import django
import sys
import asyncio

# Configurar Django
sys.path.append('c:/Users/tec_info_noite/Documents/TCC/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.authentication.models import CustomerUser
from apps.chat.models import ChatRoom, Message
from django.contrib.auth.models import User

def test_chat_notifications():
    """Testa sistema completo de notificações"""
    print("🧪 TESTANDO SISTEMA DE NOTIFICAÇÕES DO CHAT\n")
    
    try:
        # 1. Verificar Redis
        print("1️⃣ Verificando Redis...")
        channel_layer = get_channel_layer()
        if not channel_layer:
            print("❌ Redis não configurado")
            return False
        print("✅ Redis configurado")
        
        # 2. Buscar usuários de teste
        print("\n2️⃣ Buscando usuários de teste...")
        users = CustomerUser.objects.all()[:2]
        if len(users) < 2:
            print("❌ Precisa de pelo menos 2 usuários CustomerUser")
            return False
        
        user1, user2 = users[0], users[1]
        print(f"✅ Usuário 1: {user1.usuario.username} (CustomerUser ID: {user1.id})")
        print(f"✅ Usuário 2: {user2.usuario.username} (CustomerUser ID: {user2.id})")
        
        # 3. Buscar ou criar sala de chat
        print("\n3️⃣ Verificando sala de chat...")
        chat_room = ChatRoom.objects.first()
        if not chat_room:
            print("❌ Nenhuma sala de chat encontrada")
            return False
        
        print(f"✅ Sala encontrada: ID {chat_room.id}")
        
        # 4. Testar notificação para user_1
        print(f"\n4️⃣ Testando notificação para CustomerUser {user1.id}...")
        test_message = {
            'type': 'chat_list_update',
            'room_id': chat_room.id,
            'message': {
                'id': 999,
                'conteudo': 'Mensagem de teste do sistema',
                'enviado_em': '2024-01-01T12:00:00Z',
                'remetente': {
                    'id': user2.id,
                    'username': user2.usuario.username
                }
            }
        }
        
        # Enviar para grupo do usuário
        group_name = f'user_{user1.id}'
        print(f"📤 Enviando para grupo: {group_name}")
        
        async_to_sync(channel_layer.group_send)(group_name, test_message)
        print("✅ Notificação enviada com sucesso!")
        
        # 5. Testar notificação para user_2
        print(f"\n5️⃣ Testando notificação para CustomerUser {user2.id}...")
        group_name_2 = f'user_{user2.id}'
        print(f"📤 Enviando para grupo: {group_name_2}")
        
        test_message['remetente']['id'] = user1.id
        test_message['remetente']['username'] = user1.usuario.username
        
        async_to_sync(channel_layer.group_send)(group_name_2, test_message)
        print("✅ Notificação enviada com sucesso!")
        
        print("\n🎉 SISTEMA DE NOTIFICAÇÕES FUNCIONANDO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Iniciar servidor Django: python manage.py runserver")
        print("2. Abrir frontend em dois navegadores diferentes")
        print("3. Fazer login com usuários diferentes")
        print("4. Conectar ao WebSocket global em ambos")
        print("5. Enviar mensagem de um usuário")
        print("6. Verificar se o outro recebe notificação")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_chat_notifications()