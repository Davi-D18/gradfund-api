#!/usr/bin/env python3
"""
Script para testar decodificação de tokens JWT
"""
import os
import django
import sys

# Configurar Django
sys.path.append('/home/ld/Documentos/projetos/Senai/Back-end/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken

def test_token_decoding():
    """Testa a decodificação de tokens para diferentes usuários"""
    print("🔍 TESTE DE DECODIFICAÇÃO DE TOKENS JWT\n")
    
    # Listar todos os usuários
    users = User.objects.all()
    print(f"📋 Usuários no sistema:")
    for user in users:
        print(f"   - ID: {user.id}, Username: {user.username}, Email: {user.email}")
    
    print("\n" + "="*60)
    
    # Testar token para cada usuário
    for user in users:
        print(f"\n🧪 TESTANDO USUÁRIO: {user.username} (ID: {user.id})")
        
        try:
            # Gerar token
            token = AccessToken.for_user(user)
            token_str = str(token)
            
            print(f"   ✅ Token gerado: {token_str[:50]}...")
            
            # Decodificar token
            decoded_data = jwt_decode(token_str, settings.SECRET_KEY, algorithms=["HS256"])
            
            print(f"   📊 Dados decodificados:")
            print(f"      - user_id: {decoded_data.get('user_id')} (tipo: {type(decoded_data.get('user_id'))})")
            print(f"      - username: {decoded_data.get('username')}")
            print(f"      - exp: {decoded_data.get('exp')}")
            print(f"      - iat: {decoded_data.get('iat')}")
            
            # Verificar se user_id bate
            token_user_id = decoded_data.get('user_id')
            if isinstance(token_user_id, str):
                token_user_id = int(token_user_id)
            
            if token_user_id == user.id:
                print(f"   ✅ CORRETO: user_id do token ({token_user_id}) == user.id ({user.id})")
            else:
                print(f"   ❌ ERRO: user_id do token ({token_user_id}) != user.id ({user.id})")
                
        except Exception as e:
            print(f"   ❌ ERRO ao processar usuário {user.username}: {str(e)}")
    
    print("\n" + "="*60)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_token_decoding()