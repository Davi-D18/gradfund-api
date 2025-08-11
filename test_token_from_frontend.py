#!/usr/bin/env python3
import os
import django
import sys

sys.path.append('/home/ld/Documentos/projetos/Senai/Back-end/gradfund-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from jwt import decode as jwt_decode
from django.conf import settings

def test_token_from_frontend():
    print("🔍 TESTE DE TOKEN DO FRONTEND\n")
    
    # Cole aqui o token que o frontend está enviando
    token = input("Cole o token que o frontend está enviando: ").strip()
    
    if not token:
        print("❌ Token vazio")
        return
    
    try:
        decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        print(f"✅ Token decodificado com sucesso:")
        print(f"   - user_id: {decoded_data.get('user_id')}")
        print(f"   - username: {decoded_data.get('username')}")
        print(f"   - exp: {decoded_data.get('exp')}")
        print(f"   - iat: {decoded_data.get('iat')}")
        
        user_id = decoded_data.get('user_id')
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        print(f"\n🎯 RESULTADO: Token é do usuário ID {user_id}")
        
    except Exception as e:
        print(f"❌ Erro ao decodificar token: {e}")

if __name__ == "__main__":
    test_token_from_frontend()