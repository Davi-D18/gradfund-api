#!/usr/bin/env python3
"""
Script para testar se há problema com instâncias do Consumer
"""
import os
import django
import sys

# Configurar Django
sys.path.append('/home/ld/Documentos/projetos/Senai/Back-end/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.chat.consumers.chat_consumer import active_connections, ChatConsumer
from django.contrib.auth.models import User

def test_consumer_instances():
    """Testa se há problema com instâncias do Consumer"""
    print("🧪 TESTE DE INSTÂNCIAS DO CONSUMER\n")
    
    # Limpar conexões
    active_connections.clear()
    print("🧹 Conexões limpas")
    
    # Buscar usuários
    try:
        user_2 = User.objects.get(id=2)
        user_3 = User.objects.get(id=3)
        print(f"👤 Usuário 2: {user_2.username}")
        print(f"👤 Usuário 3: {user_3.username}")
    except User.DoesNotExist as e:
        print(f"❌ Usuário não encontrado: {e}")
        return
    
    print("\n" + "="*60)
    
    # Criar instâncias do Consumer
    print("🏗️ CRIANDO INSTÂNCIAS DO CONSUMER:")
    
    consumer_1 = ChatConsumer()
    consumer_1.user = user_2
    consumer_1.user_id = user_2.id
    consumer_1.room_id = 1
    print(f"Consumer 1: user_id = {consumer_1.user_id}, username = {consumer_1.user.username}")
    
    consumer_2 = ChatConsumer()
    consumer_2.user = user_3
    consumer_2.user_id = user_3.id
    consumer_2.room_id = 1
    print(f"Consumer 2: user_id = {consumer_2.user_id}, username = {consumer_2.user.username}")
    
    print("\n" + "="*60)
    
    # Verificar se há compartilhamento de estado
    print("🔍 VERIFICAÇÃO DE COMPARTILHAMENTO DE ESTADO:")
    
    print(f"Consumer 1 após criar Consumer 2:")
    print(f"   - user_id: {consumer_1.user_id}")
    print(f"   - user.id: {consumer_1.user.id}")
    print(f"   - user.username: {consumer_1.user.username}")
    
    print(f"Consumer 2:")
    print(f"   - user_id: {consumer_2.user_id}")
    print(f"   - user.id: {consumer_2.user.id}")
    print(f"   - user.username: {consumer_2.user.username}")
    
    # Verificar se são diferentes
    if consumer_1.user_id != consumer_2.user_id:
        print("✅ CORRETO: Instâncias têm usuários diferentes")
    else:
        print("❌ PROBLEMA: Instâncias compartilham o mesmo usuário")
    
    print("\n" + "="*60)
    
    # Verificar conexões ativas
    print("🔗 CONEXÕES ATIVAS:")
    print(f"Total: {len(active_connections)}")
    for key, data in active_connections.items():
        print(f"   - {key}: {data}")
    
    print("\n" + "="*60)
    
    # Testar se há variáveis de classe
    print("🔍 VERIFICAÇÃO DE VARIÁVEIS DE CLASSE:")
    
    # Verificar se há atributos de classe que podem causar problema
    class_attrs = [attr for attr in dir(ChatConsumer) if not attr.startswith('_') and not callable(getattr(ChatConsumer, attr))]
    
    if class_attrs:
        print("⚠️ Atributos de classe encontrados:")
        for attr in class_attrs:
            print(f"   - {attr}: {getattr(ChatConsumer, attr)}")
    else:
        print("✅ Nenhum atributo de classe problemático encontrado")

if __name__ == "__main__":
    test_consumer_instances()