#!/usr/bin/env python3
"""
Script para testar conexão Redis
"""
import os
import django
import sys

# Configurar Django
sys.path.append('c:/Users/tec_info_noite/Documents/TCC/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def test_redis_connection():
    """Testa conexão com Redis"""
    print("🔍 TESTANDO CONEXÃO REDIS\n")
    
    try:
        channel_layer = get_channel_layer()
        
        if channel_layer is None:
            print("❌ ERRO: Channel layer não configurado")
            return False
        
        print(f"✅ Channel layer encontrado: {channel_layer.__class__.__name__}")
        
        # Teste básico de envio/recebimento
        test_channel = 'test-channel'
        test_message = {'type': 'test.message', 'text': 'Hello Redis!'}
        
        print("📤 Enviando mensagem de teste...")
        async_to_sync(channel_layer.send)(test_channel, test_message)
        print("✅ Mensagem enviada com sucesso!")
        
        # Teste de group
        test_group = 'test-group'
        print("📤 Testando group send...")
        async_to_sync(channel_layer.group_send)(test_group, test_message)
        print("✅ Group send funcionando!")
        
        print("\n🎉 REDIS FUNCIONANDO CORRETAMENTE!")
        return True
        
    except Exception as e:
        print(f"❌ ERRO na conexão Redis: {str(e)}")
        print("\n💡 SOLUÇÕES:")
        print("1. Instalar Redis:")
        print("   - Windows: https://github.com/microsoftarchive/redis/releases")
        print("   - Docker: docker run -d -p 6379:6379 redis:alpine")
        print("2. Verificar se Redis está rodando: redis-cli ping")
        print("3. Verificar configuração em core/settings/base.py")
        return False

if __name__ == "__main__":
    test_redis_connection()